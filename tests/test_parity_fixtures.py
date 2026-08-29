import pytest
from tests.utils.parity_harness import ParityFixture, run_parity

def verify_comparison(comparison):
    if comparison.status == "SKIP":
        pytest.skip(comparison.skip_reason)
    assert comparison.status == "PASS", f"Parity comparison failed with mismatches: {comparison.mismatches}"

def test_milestone_a_basic_move():
    """Fixture A: Basic PIC X / PIC 9 MOVE verification."""
    cobol_code = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. MOVEPROG.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-STR-A PIC X(10) VALUE "ABC".
       01 WS-STR-B PIC X(5).
       01 WS-NUM-A PIC 9(4) VALUE 123.
       01 WS-NUM-B PIC 9(6).
       PROCEDURE DIVISION.
           MOVE WS-STR-A TO WS-STR-B
           MOVE WS-NUM-A TO WS-NUM-B
           DISPLAY WS-STR-B
           DISPLAY WS-NUM-B
           GOBACK.
"""
    fixture = ParityFixture(
        name="milestone_a_basic_move",
        program_name="MOVEPROG",
        cobol_code=cobol_code
    )
    res = run_parity(fixture)
    verify_comparison(res)

def test_milestone_a_integer_compute_add():
    """Fixture B: Basic COMPUTE and ADD verification (integer only)."""
    cobol_code = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. ARITHPROG.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-NUM-A PIC 9(4) VALUE 10.
       01 WS-NUM-B PIC 9(4) VALUE 20.
       01 WS-NUM-C PIC 9(4) VALUE 0.
       PROCEDURE DIVISION.
           ADD WS-NUM-A TO WS-NUM-B GIVING WS-NUM-C
           DISPLAY WS-NUM-C
           COMPUTE WS-NUM-C = WS-NUM-A * 5 + WS-NUM-B
           DISPLAY WS-NUM-C
           GOBACK.
"""
    fixture = ParityFixture(
        name="milestone_a_integer_compute_add",
        program_name="ARITHPROG",
        cobol_code=cobol_code
    )
    res = run_parity(fixture)
    verify_comparison(res)

def test_milestone_a_line_sequential_file():
    """Fixture C: Simple line-sequential output file using UTF-8/ASCII records."""
    cobol_code = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. SEQFILEPROG.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT OUT-FILE ASSIGN TO "OUTFILE.TXT"
           ORGANIZATION IS LINE SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD OUT-FILE.
       01 OUT-REC PIC X(20).
       PROCEDURE DIVISION.
           OPEN OUTPUT OUT-FILE
           MOVE "HELLO WORLD 1" TO OUT-REC
           WRITE OUT-REC
           MOVE "HELLO WORLD 2" TO OUT-REC
           WRITE OUT-REC
           CLOSE OUT-FILE
           DISPLAY "FILE WRITTEN"
           GOBACK.
"""
    fixture = ParityFixture(
        name="milestone_a_line_sequential_file",
        program_name="SEQFILEPROG",
        cobol_code=cobol_code,
        declared_outputs=["OUTFILE.TXT"]
    )
    res = run_parity(fixture)
    verify_comparison(res)

import json
import os

def load_fixtures_spec():
    spec_path = os.path.join(os.path.dirname(__file__), "fixtures_spec.json")
    with open(spec_path, "r", encoding="utf-8") as f:
        return json.load(f)

FIXTURES = load_fixtures_spec()

def generate_cobol_source(spec):
    lines = [
        "       IDENTIFICATION DIVISION.",
        f"       PROGRAM-ID. {spec['program_name']}.",
        "       DATA DIVISION.",
        "       WORKING-STORAGE SECTION.",
        "       01 WS-GROUP."
    ]
    
    for i, var in enumerate(spec["variables"]):
        pic_clause = f"PIC {var['pic']}" if var.get("pic") else ""
        redef_clause = f"REDEFINES {var['redefines']}" if var.get("redefines") else ""
        usage = var.get("usage", "")
        usage_clause = f"USAGE {usage}" if usage else ""
        sign_clause = ""
        if (var.get("signed", False) or (pic_clause and pic_clause.startswith("PIC S"))) and usage not in ("COMP-3", "PACKED-DECIMAL"):
            sign_pos = var.get("sign_position", "TRAILING")
            sign_sep = "SEPARATE CHARACTER" if var.get("sign_separate", False) else ""
            sign_clause = f"SIGN IS {sign_pos} {sign_sep}"
            
        parts = [p for p in ["05", var['name'], redef_clause, pic_clause, usage_clause, sign_clause] if p]
        lines.append("          " + " ".join(parts) + ".")
        if i < len(spec["variables"]) - 1:
            next_var = spec["variables"][i + 1]
            if not next_var.get("redefines"):
                lines.append("          05 FILLER PIC X VALUE '|'.")
            
    lines.append("       PROCEDURE DIVISION.")
    # Initialize all variables, but skip redefined targets to avoid initialisation overlap errors in compiler
    init_vars = [var["name"] for var in spec["variables"] if not var.get("redefines")]
    var_names = " ".join(init_vars)
    lines.append(f"           INITIALIZE {var_names}.")
    
    for var in spec["variables"]:
        val = var.get("value")
        if val:
            lines.append(f"           MOVE {val} TO {var['name']}.")
            
    for stmt in spec["statements"]:
        lines.append(f"           {stmt}.")
        
    lines.append("           GOBACK.")
    return "\n".join(lines)

@pytest.mark.parametrize("spec", FIXTURES, ids=lambda s: s["name"])
def test_milestone_b_parity(spec):
    name = spec["name"]
    cobol_code = generate_cobol_source(spec)
    
    fixture = ParityFixture(
        name=name,
        program_name=spec["program_name"],
        cobol_code=cobol_code
    )
    
    res = run_parity(fixture)
    if res.status == "SKIP":
        pytest.skip(res.skip_reason)
    assert res.status == "PASS", f"Parity comparison failed with mismatches: {res.mismatches}"

def test_unsupported_precision_guard_unit():
    spec = {
        "name": "milestone_b_unsupported_precision_guard",
        "program_name": "UNSUPPGD",
        "variables": [
            {"name": "A", "pic": "9(30)V9(5)", "value": "0"}
        ],
        "statements": [
            "DIVIDE 1 BY 3 GIVING A",
            "DISPLAY WS-GROUP"
        ]
    }
    cobol_code = generate_cobol_source(spec)
    fixture = ParityFixture(
        name=spec["name"],
        program_name=spec["program_name"],
        cobol_code=cobol_code
    )
    
    from tests.utils.parity_harness import run_java_transpiled, run_cobol_baseline
    import tempfile
    import shutil
    
    temp_root = tempfile.mkdtemp(prefix="parity_unsupported_precision_")
    try:
        cobol_run_dir = os.path.join(temp_root, "cobol")
        java_run_dir = os.path.join(temp_root, "java")
        os.makedirs(cobol_run_dir, exist_ok=True)
        os.makedirs(java_run_dir, exist_ok=True)
        
        cobol_res = run_cobol_baseline(fixture, cobol_run_dir)
        assert cobol_res.termination_status != "error", f"COBOL compilation failed: {cobol_res.error_message}"
        
        java_res = run_java_transpiled(fixture, java_run_dir)
        assert b"UnsupportedPrecisionException" in java_res.stderr or b"UnsupportedPrecisionException" in java_res.stdout
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)

def test_unchecked_and_abs_assign_result_semantics_unit():
    from tests.utils.parity_harness import run_java_transpiled, run_cmd_bytes, PARITY_JDK_IMAGE
    import tempfile
    import shutil
    
    java_src = """package com.systema.modernized.native_gen;
import java.math.BigDecimal;
import com.systema.modernized.runtime.*;

public class Testuncheckedandabs {
    public void execute() {
        // Test (a): AssignResult.sizeError is set true under UNCHECKED when high-order digits are lost
        CobolNumericSpec specA = new CobolNumericSpec(false, 3, 0, CobolUsage.DISPLAY);
        CobolNumeric varA = new CobolNumeric(BigDecimal.ZERO, specA);
        AssignResult resA = varA.assign(new BigDecimal("1234"), CobolRoundingMode.TRUNCATION, SizeErrorPolicy.UNCHECKED);
        if (!resA.sizeError) {
            throw new RuntimeException("Test A failed: sizeError was false under UNCHECKED");
        }
        if (resA.storedValue.compareTo(new BigDecimal("234")) != 0) {
            throw new RuntimeException("Test A failed: storedValue was not truncated to 234");
        }

        // Test (b): abs() is applied BEFORE the high-order bounds check for unsigned receivers
        CobolNumericSpec specB = new CobolNumericSpec(false, 3, 0, CobolUsage.DISPLAY);
        CobolNumeric varB = new CobolNumeric(BigDecimal.ZERO, specB);
        AssignResult resB = varB.assign(new BigDecimal("-5"), CobolRoundingMode.TRUNCATION, SizeErrorPolicy.UNCHECKED);
        if (resB.sizeError) {
            throw new RuntimeException("Test B failed: sizeError was true for unsigned receiver with negative input");
        }
        if (resB.storedValue.compareTo(new BigDecimal("5")) != 0) {
            throw new RuntimeException("Test B failed: storedValue was not 5");
        }

        System.out.println("SEMANTICS_OK");
    }

    public static void main(String[] args) {
        new Testuncheckedandabs().execute();
    }
}
"""
    dummy_fixture = ParityFixture(
        name="dummy",
        program_name="Dummy",
        cobol_code=""
    )
    
    temp_root = tempfile.mkdtemp(prefix="unchecked_abs_semantics_")
    try:
        java_run_dir = os.path.join(temp_root, "java")
        os.makedirs(java_run_dir, exist_ok=True)
        
        # Call run_java_transpiled with dummy to copy format and runtime helpers
        run_java_transpiled(dummy_fixture, java_run_dir)
        
        # Write Testuncheckedandabs.java to native_gen/ package
        pkg_dir = os.path.join(java_run_dir, "com", "systema", "modernized", "native_gen")
        os.makedirs(pkg_dir, exist_ok=True)
        with open(os.path.join(pkg_dir, "Testuncheckedandabs.java"), "w", encoding="utf-8") as f:
            f.write(java_src)
            
        # Compile inside Docker
        run_dir_abs = os.path.abspath(java_run_dir).replace("\\", "/")
        inner_compile = (
            "javac -cp /run "
            "/run/com/systema/modernized/JclExecutionContext.java "
            "/run/com/systema/modernized/CicsProgramRegistry.java "
            "/run/com/systema/modernized/SpringContextHelper.java "
            "/run/com/systema/modernized/CobolFormatHelper.java "
            "/run/com/systema/modernized/runtime/*.java "
            "/run/com/systema/modernized/native_gen/Testuncheckedandabs.java"
        )
        compile_cmd = [
            "docker", "run", "--rm",
            "-v", f"{run_dir_abs}:/run",
            "-w", "/run",
            PARITY_JDK_IMAGE,
            "sh", "-c", inner_compile
        ]
        rc, out, err, term = run_cmd_bytes(compile_cmd)
        assert rc == 0, f"Compilation failed: {err.decode('utf-8')}"
        
        # Run inside Docker
        run_cmd = [
            "docker", "run", "--rm",
            "-v", f"{run_dir_abs}:/run",
            "-w", "/run",
            PARITY_JDK_IMAGE,
            "java", "-cp", "/run", "com.systema.modernized.native_gen.Testuncheckedandabs"
        ]
        rc, out, err, term = run_cmd_bytes(run_cmd)
        assert rc == 0, f"Execution failed: {err.decode('utf-8')}"
        assert b"SEMANTICS_OK" in out
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)

def test_compiler_fingerprint_drift():
    """Assert that the running Docker image matches the pinned GnuCOBOL compiler fingerprint."""
    from tests.utils.check_fingerprint import EXPECTED_HASH, IMAGE, PARITY_ALLOW_SKIP
    import subprocess
    import hashlib
    
    try:
        docker_check = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
        if docker_check.returncode != 0:
            if PARITY_ALLOW_SKIP:
                pytest.skip("Docker not available and PARITY_ALLOW_SKIP is true")
            else:
                pytest.fail("Docker not available and PARITY_ALLOW_SKIP is false")
    except Exception:
        if PARITY_ALLOW_SKIP:
            pytest.skip("Docker check failed and PARITY_ALLOW_SKIP is true")
        else:
            pytest.fail("Docker check failed and PARITY_ALLOW_SKIP is false")
            
    cmd = ["docker", "run", "--rm", IMAGE, "cobc", "--info"]
    res = subprocess.run(cmd, capture_output=True, timeout=30)
    assert res.returncode == 0, f"GnuCOBOL check exited with {res.returncode}: {res.stderr.decode('utf-8')}"
    
    h = hashlib.sha256(res.stdout).hexdigest().lower()
    assert h == EXPECTED_HASH, f"GnuCOBOL fingerprint mismatch! Expected {EXPECTED_HASH}, got {h}"


def test_milestone_b_fixed_binary_file_io():
    """Fixture D: Fixed-length raw byte binary sequential file IO with COMP-3 and signed trailing-separate zoned decimal."""
    cobol_code = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. BINIO.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT BIN-FILE ASSIGN TO "BINFILE.DAT"
           ORGANIZATION IS SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD BIN-FILE.
       01 BIN-REC.
          05 FIELD-COMP3 PIC S9(4)V99 COMP-3.
          05 FIELD-ZONED PIC S9(4) SIGN IS TRAILING SEPARATE CHARACTER.
       WORKING-STORAGE SECTION.
       01 WS-VAR.
          05 WS-COMP3 PIC S9(4)V99 COMP-3.
          05 WS-ZONED PIC S9(4) SIGN IS TRAILING SEPARATE CHARACTER.
       PROCEDURE DIVISION.
           OPEN OUTPUT BIN-FILE.
           MOVE -12.34 TO WS-COMP3.
           MOVE -5678 TO WS-ZONED.
           MOVE WS-COMP3 TO FIELD-COMP3.
           MOVE WS-ZONED TO FIELD-ZONED.
           WRITE BIN-REC.
           CLOSE BIN-FILE.
           
           INITIALIZE BIN-REC.
           OPEN INPUT BIN-FILE.
           READ BIN-FILE.
           CLOSE BIN-FILE.
           DISPLAY FIELD-COMP3.
           DISPLAY FIELD-ZONED.
           GOBACK.
"""
    fixture = ParityFixture(
        name="milestone_b_fixed_binary_file_io",
        program_name="BINIO",
        cobol_code=cobol_code,
        declared_outputs=["BINFILE.DAT"]
    )
    res = run_parity(fixture)
    verify_comparison(res)
def test_milestone_b_integer_fast_path_audit():
    """Fixture E: Fast-path primitive Integer and Long variables parity validation."""
    cobol_code = """       IDENTIFICATION DIVISION.
           PROGRAM-ID. FPFAST.
           DATA DIVISION.
           WORKING-STORAGE SECTION.
           01 WS-VARS.
              05 WS-INT PIC S9(9).
              05 WS-LONG PIC S9(15).
           PROCEDURE DIVISION.
               MOVE 123456789 TO WS-INT.
               MOVE -987654321012345 TO WS-LONG.
               DISPLAY WS-INT.
               DISPLAY WS-LONG.
               ADD 10 TO WS-INT.
               SUBTRACT 100 FROM WS-LONG.
               DISPLAY WS-INT.
               DISPLAY WS-LONG.
               GOBACK.
"""
    fixture = ParityFixture(
        name="milestone_b_integer_fast_path_audit",
        program_name="FPFAST",
        cobol_code=cobol_code
    )
    res = run_parity(fixture)
    verify_comparison(res)

