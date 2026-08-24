import os
import json
import shutil
import tempfile
import pytest
from modernize.lexer import CobolLexer
from modernize.parser import CobolParser
from modernize.jcl_parser import JclParser
from modernize.native_pipeline import NativePipeline

def test_jcl_symbol_substitution():
    jcl_content = """//TESTJOB  JOB (ACCT)
//SET1     SET VAR1='MY.VAL1'
//SET2     SET VAR2=&VAR1
//STEP1    EXEC PGM=PROG1
//DD1      DD DSN=&VAR2..DATA,DISP=SHR
//DD2      DD DSN=&&TEMP,DISP=NEW
"""
    parser = JclParser(jcl_content, "/dummy/repo")
    job = parser.parse()
    
    assert job.symbols["VAR1"] == "MY.VAL1"
    assert job.symbols["VAR2"] == "MY.VAL1"
    
    step1 = job.steps[0]
    dd1 = step1.dds["DD1"]
    dd2 = step1.dds["DD2"]
    
    assert dd1.dsn == "MY.VAL1.DATA"
    # Should preserve temporary dataset semantics (&&)
    assert dd2.dsn == "&&TEMP"

def test_jcl_symbol_unresolved_diag():
    jcl_content = """//TESTJOB  JOB (ACCT)
//STEP1    EXEC PGM=PROG1
//DD1      DD DSN=&UNRESOLVED.DATA,DISP=SHR
"""
    parser = JclParser(jcl_content, "/dummy/repo")
    parser.parse()
    diags = parser.diagnostics
    assert len(diags) > 0
    assert "JCL_UNRESOLVED_SYMBOL" in diags[0]["reason"]

def test_jcl_symbols_e2e():
    repo_dir = os.path.join("tests", "repos", "JCLSYMBOL01")
    temp_out = tempfile.mkdtemp()
    
    # Pre-seed MY.INPUT.DATA inside the temp directory mapped output or repo
    # Wait, the JclExecutionContext uses DD assignments.
    # At execution runtime, the test needs MY.INPUT.DATA and &&MYTEMP data to exist.
    try:
        # Pre-seed expected baseline stdout.txt
        expected_stdout = (
            "=== START JCL JOB: JCLSYMBOL01 ===\n"
            "=== EXECUTE STEP: STEP1 (PGM: COBPROG1) ===\n"
            + "INPUT DATA LINE 1".ljust(80) + "\n"
            + "INPUT DATA LINE 2".ljust(80) + "\n"
            + "STEP STEP1 FINISHED WITH RC: 0\n"
            "=== EXECUTE STEP: STEP2.PROCSTEP (PGM: COBPROG1) ===\n"
            + "TEMP DATA LINE 1".ljust(80) + "\n"
            + "STEP STEP2.PROCSTEP FINISHED WITH RC: 0\n"
            "=== END JCL JOB: JCLSYMBOL01 ===\n"
        )
        
        baseline_dir = os.path.join(temp_out, "baseline", "legacy")
        os.makedirs(baseline_dir, exist_ok=True)
        with open(os.path.join(baseline_dir, "stdout.txt"), "w", encoding="utf-8") as fh:
            fh.write(expected_stdout)
            
        # Create input file in workspace or temp dir
        # In modernize/native_pipeline.py: L804:
        # copy dataset files from the repo "data" dir to output "results/native"
        os.makedirs(os.path.join(temp_out, "results", "native"), exist_ok=True)
        with open(os.path.join(temp_out, "results", "native", "MY.INPUT.DATA"), "w", encoding="utf-8") as fh:
            fh.write("INPUT DATA LINE 1\nINPUT DATA LINE 2\n")
        with open(os.path.join(temp_out, "results", "native", "MYTEMP"), "w", encoding="utf-8") as fh:
            fh.write("TEMP DATA LINE 1\n")
            
        p = NativePipeline(repo_dir, temp_out)
        p.run_legacy_baseline = lambda: None
        verdict = p.run()
        
        # Verify success
        if verdict != "NATIVE_JAVA_VERIFIED":
            obs_path = os.path.join(temp_out, "native", "target", "generated", "native_execution_observation.json")
            if os.path.exists(obs_path):
                with open(obs_path, "r") as fh:
                    print("=== NATIVE RUN OBSERVATION ===")
                    print(fh.read())
        assert verdict == "NATIVE_JAVA_VERIFIED", f"JCL Symbol E2E pipeline failed with verdict: {verdict}"
        
    finally:
        shutil.rmtree(temp_out, ignore_errors=True)
