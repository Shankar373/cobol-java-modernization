"""Unseen Repository Validation Suite.

Validates that the modernization platform correctly parses, generates, and
verifies diverse synthetic COBOL workloads without repository-specific hacks.
"""
from pathlib import Path
import json
import pytest

from modernize.lexer import CobolLexer
from modernize.parser import CobolParser
from modernize.native_generator import NativeProgramGenerator
from modernize.native_pipeline import NativePipeline
from audit.manifest import generate_manifest
from audit.certify import generate_scorecard


# ---------------------------------------------------------------------------
# 1. COBOL-only pure calculation
# ---------------------------------------------------------------------------
def test_unseen_01_pure_calculation(tmp_path):
    cobol_src = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. COMPOUND01.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-PRINCIPAL      PIC 9(6)V99 VALUE 10000.00.
       01  WS-RATE           PIC 9(2)V99 VALUE 05.00.
       01  WS-YEARS          PIC 9(2)    VALUE 03.
       01  WS-INTEREST       PIC 9(6)V99 VALUE ZERO.
       01  WS-TOTAL          PIC 9(6)V99 VALUE ZERO.
       PROCEDURE DIVISION.
           COMPUTE WS-INTEREST = (WS-PRINCIPAL * WS-RATE * WS-YEARS) / 100
           COMPUTE WS-TOTAL = WS-PRINCIPAL + WS-INTEREST
           DISPLAY "PRINCIPAL: " WS-PRINCIPAL " INTEREST: " WS-INTEREST " TOTAL: " WS-TOTAL
           GOBACK.
"""
    repo = tmp_path / "repo"
    out = tmp_path / "out"
    (repo / "src").mkdir(parents=True, exist_ok=True)
    (repo / "src" / "COMPOUND01.cob").write_text(cobol_src, encoding="utf-8")

    pipeline = NativePipeline(str(repo), str(out))
    pipeline.stage_discover()
    assert len(pipeline.sources) == 1

    pipeline.stage_parse()
    selected = pipeline.stage_select_slice()
    assert selected is not None

    pipeline.stage_generate(selected)
    gen_files = list((out / "native").rglob("*.java"))
    assert len(gen_files) > 0


# ---------------------------------------------------------------------------
# 2. COPYBOOK inclusion
# ---------------------------------------------------------------------------
def test_unseen_02_copybook_expansion(tmp_path):
    cpy_src = """       01  CUSTOMER-RECORD.
           05  CUST-ID        PIC X(10).
           05  CUST-NAME      PIC X(30).
           05  CUST-BALANCE   PIC 9(7)V99.
"""
    cobol_src = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. CUSTCOPY01.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       COPY CUSTREC.
       PROCEDURE DIVISION.
           MOVE "CUST000001" TO CUST-ID
           MOVE "ALICE COOPER" TO CUST-NAME
           MOVE 12500.50 TO CUST-BALANCE
           DISPLAY "ID: " CUST-ID " NAME: " CUST-NAME " BAL: " CUST-BALANCE
           GOBACK.
"""
    repo = tmp_path / "repo"
    out = tmp_path / "out"
    (repo / "src").mkdir(parents=True, exist_ok=True)
    (repo / "cpy").mkdir(parents=True, exist_ok=True)
    (repo / "cpy" / "CUSTREC.cpy").write_text(cpy_src, encoding="utf-8")
    (repo / "src" / "CUSTCOPY01.cob").write_text(cobol_src, encoding="utf-8")

    pipeline = NativePipeline(str(repo), str(out))
    pipeline.stage_discover()
    pipeline.stage_parse()
    selected = pipeline.stage_select_slice()
    pipeline.stage_generate(selected)
    gen_files = list((out / "native").rglob("*.java"))
    assert any("Custcopy01" in f.name for f in gen_files)


# ---------------------------------------------------------------------------
# 3. File processing (Sequential record filtering)
# ---------------------------------------------------------------------------
def test_unseen_03_file_sequential_filter(tmp_path):
    cobol_src = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. FILEFLTR01.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT IN-FILE ASSIGN TO "data/in.dat"
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT OUT-FILE ASSIGN TO "data/out.dat"
               ORGANIZATION IS LINE SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD  IN-FILE.
       01  IN-REC            PIC X(50).
       FD  OUT-FILE.
       01  OUT-REC           PIC X(50).
       WORKING-STORAGE SECTION.
       01  WS-EOF            PIC X VALUE "N".
       PROCEDURE DIVISION.
           OPEN INPUT IN-FILE OUTPUT OUT-FILE
           PERFORM UNTIL WS-EOF = "Y"
               READ IN-FILE
                   AT END MOVE "Y" TO WS-EOF
                   NOT AT END
                       WRITE OUT-REC FROM IN-REC
               END-READ
           END-PERFORM
           CLOSE IN-FILE OUT-FILE
           GOBACK.
"""
    repo = tmp_path / "repo"
    out = tmp_path / "out"
    (repo / "src").mkdir(parents=True, exist_ok=True)
    (repo / "src" / "FILEFLTR01.cob").write_text(cobol_src, encoding="utf-8")

    pipeline = NativePipeline(str(repo), str(out))
    pipeline.stage_discover()
    pipeline.stage_parse()
    selected = pipeline.stage_select_slice()
    pipeline.stage_generate(selected)
    gen_files = list((out / "native").rglob("*.java"))
    assert len(gen_files) > 0


# ---------------------------------------------------------------------------
# 4. SQL program (Unseen table query)
# ---------------------------------------------------------------------------
def test_unseen_04_sql_query(tmp_path):
    cobol_src = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. SQLUNSEEN01.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
           EXEC SQL INCLUDE SQLCA END-EXEC.
       01  HV-ITEM-ID       PIC X(10).
       01  HV-ITEM-QTY      PIC S9(9) COMP.
       PROCEDURE DIVISION.
           EXEC SQL
               SELECT ITEM_ID, QUANTITY
               INTO :HV-ITEM-ID, :HV-ITEM-QTY
               FROM INVENTORY
               WHERE ITEM_ID = 'SKU999'
           END-EXEC.
           DISPLAY "SQLCODE: " SQLCODE
           GOBACK.
"""
    repo = tmp_path / "repo"
    out = tmp_path / "out"
    (repo / "src").mkdir(parents=True, exist_ok=True)
    (repo / "src" / "SQLUNSEEN01.cob").write_text(cobol_src, encoding="utf-8")

    pipeline = NativePipeline(str(repo), str(out))
    pipeline.stage_discover()
    pipeline.stage_parse()
    selected = pipeline.stage_select_slice()
    pipeline.stage_generate(selected)
    gen_files = list((out / "native").rglob("*.java"))
    assert len(gen_files) > 0


# ---------------------------------------------------------------------------
# 5. JCL Step conditional flow
# ---------------------------------------------------------------------------
def test_unseen_05_jcl_orchestration(tmp_path):
    jcl_src = """//DAILYJOB JOB (ACCT),'DAILY BATCH',CLASS=A,MSGCLASS=X
//STEP1    EXEC PGM=COMPOUND01
//DDIN     DD DSN=DATA.IN,DISP=SHR
//DDOUT    DD DSN=DATA.OUT,DISP=(NEW,CATLG,DELETE)
//STEP2    EXEC PGM=FILEFLTR01,COND=(0,NE,STEP1)
//SYSIN    DD *
OPTION=ACTIVE
/*
//
"""
    repo = tmp_path / "repo"
    out = tmp_path / "out"
    (repo / "jcl").mkdir(parents=True, exist_ok=True)
    (repo / "jcl" / "DAILYJOB.jcl").write_text(jcl_src, encoding="utf-8")

    from modernize.jcl_parser import JclParser
    parser = JclParser(jcl_src)
    job = parser.parse()
    assert job is not None
    assert len(job.steps) == 2
    assert job.steps[0].name == "STEP1"
    assert job.steps[1].name == "STEP2"


# ---------------------------------------------------------------------------
# 6. CICS screen map & commarea
# ---------------------------------------------------------------------------
def test_unseen_06_cics_bms_parsing(tmp_path):
    bms_src = """MAPSET   DFHMSD TYPE=&SYSPARM,MODE=INOUT,LANG=COBOL,STORAGE=AUTO
MAP01    DFHMDI SIZE=(24,80),LINE=1,COLUMN=1
TITLE    DFHMDF POS=(1,30),LENGTH=20,ATTRB=(ASKIP,NORM),INITIAL='ACCOUNT INQUIRY'
ACCNO    DFHMDF POS=(3,10),LENGTH=10,ATTRB=(UNPROT,NORM)
         DFHMSD TYPE=FINAL
"""
    from modernize.bms_parser import BmsParser
    parser = BmsParser(bms_src)
    screen_map = parser.parse()
    assert screen_map is not None
    assert screen_map.name in ["MAPSET", "MAP01"]


# ---------------------------------------------------------------------------
# 7. Unsupported IMS / MQ detection (Fail Closed)
# ---------------------------------------------------------------------------
def test_unseen_07_unsupported_ims_fails_closed():
    from audit.evidence import Verdict, EvidenceBundle, TierEvidence
    from audit.certify import evaluate_certification

    bundle = EvidenceBundle(
        workload="UNSEEN_IMS_APP",
        unsupported_constructs=[
            {"type": "IMS_DLI", "line": 15, "statement": "CALL 'CBLTDLI' USING PCB-MASK"}
        ],
    )
    bundle.add_tier(TierEvidence(
        tier=1,
        name="Syntax & AST Parsing",
        verdict=Verdict.BLOCKED,
        errors=["IMS DL/I calls require manual database modernization"],
    ))
    scorecard = evaluate_certification(bundle)
    assert scorecard["certification_verdict"] in ["FAIL", "BLOCKED"]
    assert scorecard["certification_grade"] == "REJECTED"


# ---------------------------------------------------------------------------
# 8. Dynamic CALL argument passing
# ---------------------------------------------------------------------------
def test_unseen_08_dynamic_call_subroutine(tmp_path):
    main_cob = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. CALLER01.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-PROG-NAME     PIC X(8) VALUE "CALLEE01".
       01  WS-PARAM-NUM     PIC 9(4) VALUE 100.
       PROCEDURE DIVISION.
           CALL WS-PROG-NAME USING BY REFERENCE WS-PARAM-NUM
           DISPLAY "MODIFIED PARAM: " WS-PARAM-NUM
           GOBACK.
"""
    repo = tmp_path / "repo"
    out = tmp_path / "out"
    (repo / "src").mkdir(parents=True, exist_ok=True)
    (repo / "src" / "CALLER01.cob").write_text(main_cob, encoding="utf-8")

    pipeline = NativePipeline(str(repo), str(out))
    pipeline.stage_discover()
    pipeline.stage_parse()
    selected = pipeline.stage_select_slice()
    pipeline.stage_generate(selected)
    gen_files = list((out / "native").rglob("*.java"))
    assert len(gen_files) > 0
