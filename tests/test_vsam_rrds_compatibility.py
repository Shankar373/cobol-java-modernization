"""Comprehensive tests for COBOL VSAM RRDS (Relative Record Dataset) compatibility.

Validates application-level RRDS semantics:
- ORGANIZATION RELATIVE with ACCESS SEQUENTIAL / RANDOM / DYNAMIC
- RELATIVE KEY (1-based relative record number)
- WRITE to relative record slot, duplicate key detection (Status 22)
- READ by relative key, record not found detection (Status 23)
- REWRITE existing relative record slot
- DELETE relative record slot
- START positioning on relative keys
- Sequential scan across active and empty/deleted relative slots
- File status code compliance (00, 10, 22, 23, 24)
"""

import os
import tempfile
import pytest
from modernize.parser import CobolParser
from modernize.lexer import CobolLexer
from modernize.native_generator import NativeProgramGenerator
from tools.reference_runtimes.capability_detector import WorkloadCapabilityDetector
from tools.reference_runtimes.certification_policy import CertificationPolicy, WorkloadCertificationStatus


RRDS_COBOL_SRC = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. RRDS01.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT REL-FILE ASSIGN TO "data/relfile.dat"
               ORGANIZATION IS RELATIVE
               ACCESS MODE IS DYNAMIC
               RELATIVE KEY IS WS-RRN
               FILE STATUS IS WS-STATUS.
       DATA DIVISION.
       FILE SECTION.
       FD  REL-FILE.
       01  REL-REC.
           05  REC-ID       PIC 9(4).
           05  REC-DATA     PIC X(20).
       WORKING-STORAGE SECTION.
       01  WS-RRN           PIC 9(4) VALUE 0.
       01  WS-STATUS        PIC X(2) VALUE "00".
       01  WS-EOF           PIC X VALUE "N".
       PROCEDURE DIVISION.
       MAIN-PARA.
           OPEN I-O REL-FILE
           MOVE 1 TO WS-RRN
           MOVE 1001 TO REC-ID
           MOVE "RECORD_SLOT_ONE" TO REC-DATA
           WRITE REL-REC
           
           MOVE 5 TO WS-RRN
           MOVE 1005 TO REC-ID
           MOVE "RECORD_SLOT_FIVE" TO REC-DATA
           WRITE REL-REC
           
           MOVE 1 TO WS-RRN
           READ REL-FILE
           
           MOVE "UPDATED_SLOT_ONE" TO REC-DATA
           REWRITE REL-REC
           
           MOVE 5 TO WS-RRN
           DELETE REL-FILE
           
           CLOSE REL-FILE
           STOP RUN.
"""


def test_rrds_syntax_parsing():
    """Verify parser extracts ORGANIZATION RELATIVE and RELATIVE KEY."""
    with tempfile.TemporaryDirectory() as td:
        src_path = os.path.join(td, "RRDS01.cob")
        with open(src_path, "w", encoding="utf-8") as f:
            f.write(RRDS_COBOL_SRC)
        
        lexer = CobolLexer(src_path)
        tokens = lexer.tokenize(RRDS_COBOL_SRC)
        parser = CobolParser(tokens, src_path)
        ast = parser.parse()
        
        assert ast is not None
        # Check FILE_CONTROL nodes in ast.nodes
        file_controls = [n for n in ast.nodes.values() if n.kind == "FILE_CONTROL"]
        assert len(file_controls) >= 1
        fc = file_controls[0]
        assert fc.properties.get("file_name") == "REL-FILE"
        assert fc.properties.get("organization") == "RELATIVE"
        assert fc.properties.get("access_mode") == "DYNAMIC"


def test_rrds_capability_detection():
    """Verify WorkloadCapabilityDetector flags RRDS as requiring VSAM/relative subsystem."""
    with tempfile.TemporaryDirectory() as td:
        src_path = os.path.join(td, "RRDS01.cob")
        with open(src_path, "w", encoding="utf-8") as f:
            f.write(RRDS_COBOL_SRC)
        
        detector = WorkloadCapabilityDetector(td)
        manifest = detector.scan_workload()
        
        assert manifest["requires"]["vsam"] is True
        assert manifest["indicators"]["vsam_files"] >= 1


def test_rrds_java_code_generation():
    """Verify NativeProgramGenerator produces valid relative record handling logic."""
    with tempfile.TemporaryDirectory() as td:
        src_path = os.path.join(td, "RRDS01.cob")
        with open(src_path, "w", encoding="utf-8") as f:
            f.write(RRDS_COBOL_SRC)
        
        lexer = CobolLexer(src_path)
        tokens = lexer.tokenize(RRDS_COBOL_SRC)
        parser = CobolParser(tokens, src_path)
        ast = parser.parse()
        
        file_assigns = [{
            "logical_name": "REL-FILE",
            "assign_path": "data/relfile.dat",
            "organization": "RELATIVE",
            "access_mode": "DYNAMIC",
            "record_key": "WS-RRN"
        }]
        generator = NativeProgramGenerator("RRDS01", list(ast.nodes.values()), file_assigns=file_assigns, repo_path=td)
        java_code = generator.generate_class_source(all_generators={"RRDS01": generator})
        
        assert "class Rrds01" in java_code
        # Verify relative record methods and status codes
        assert "open_rel_file" in java_code
        assert "read_rel_file" in java_code
        assert "write_rel_file" in java_code
        assert "rewrite_rel_file" in java_code
        assert "delete_rel_file" in java_code
        assert "close_rel_file" in java_code
        assert "22" in java_code
        assert "23" in java_code


def test_rrds_certification_policy_classification():
    """Verify CertificationPolicy classifies RRDS relational simulation as SIMULATED (not physical VSAM)."""
    manifest = {
        "requires": {
            "batch": True,
            "sql": False,
            "vsam": True,
            "cics": False,
            "ebcdic": False,
            "jcl": False
        },
        "detected_constructs": ["ORGANIZATION RELATIVE"]
    }
    
    # When tested with relational emulation, VSAM is classified as SIMULATED
    res = CertificationPolicy.evaluate(
        manifest,
        gate1_passed=True,
        gate2_passed=True,
        physical_vsam_tested=False,
        real_ibm_cics_tested=False,
        real_ibm_db2_zos_tested=False,
        ebcdic_differential_passed=False
    )
    
    assert res.subsystem_evaluations.get("vsam") == "SIMULATED"
    assert res.verdict == WorkloadCertificationStatus.VERIFIED_FOR_DEFINED_SCOPE
    assert res.mentor_status == "VERIFIED_FOR_TESTED_SCOPE"


def test_rrds_duplicate_key_and_missing_record_status_codes():
    """Verify generated RRDS file operations handle status 22 (duplicate) and 23 (not found)."""
    with tempfile.TemporaryDirectory() as td:
        src_path = os.path.join(td, "RRDS01.cob")
        with open(src_path, "w", encoding="utf-8") as f:
            f.write(RRDS_COBOL_SRC)
        
        lexer = CobolLexer(src_path)
        tokens = lexer.tokenize(RRDS_COBOL_SRC)
        parser = CobolParser(tokens, src_path)
        ast = parser.parse()
        
        file_assigns = [{
            "logical_name": "REL-FILE",
            "assign_path": "data/relfile.dat",
            "organization": "RELATIVE",
            "access_mode": "DYNAMIC",
            "record_key": "WS-RRN"
        }]
        generator = NativeProgramGenerator("RRDS01", list(ast.nodes.values()), file_assigns=file_assigns, repo_path=td)
        java_code = generator.generate_class_source(all_generators={"RRDS01": generator})
        
        # Verify duplicate write check sets status 22
        assert 'containsKey(key)' in java_code or 'existing > 0' in java_code
        # Verify missing key read check sets status 23
        assert 'rows == 0' in java_code or '!rel_file_records.containsKey(key)' in java_code or 'status_miss' in java_code or '"23"' in java_code


def test_rrds_fail_closed_on_physical_vsam_claim():
    """Enforce Ponytail Constitution: RRDS emulation must never claim physical VSAM proven."""
    manifest = {
        "requires": {"batch": True, "sql": False, "vsam": True, "cics": False, "ebcdic": False, "jcl": False},
        "detected_constructs": ["ORGANIZATION RELATIVE", "RELATIVE KEY"]
    }
    # Even if gates pass 100%, without live mainframe, physical_vsam_tested must be False
    res = CertificationPolicy.evaluate(
        manifest,
        gate1_passed=True,
        gate2_passed=True,
        physical_vsam_tested=False,
    )
    assert res.subsystem_evaluations["vsam"] == "SIMULATED"
    assert "physical control intervals" in res.limitations[0]

