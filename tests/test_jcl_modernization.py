import os
import shutil
import tempfile
import pytest
import subprocess
import re
from modernize.jcl_parser import JclParser
from modernize.native_pipeline import NativePipeline

def test_jcl_parser_unit():
    jcl_path = r"c:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test\tests\repos\JCLBATCH01\src\JCLBATCH01.jcl"
    content = open(jcl_path, "r", encoding="utf-8").read()
    parser = JclParser(content, repo_dir=r"c:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test\tests\repos\JCLBATCH01")
    job = parser.parse()
    
    assert job.name == "JCLBATCH01"
    # Flat steps collected count should be 4 (STEP1, STEP2.PROCSTEP, STEPBYPS, STEP3)
    flat_steps = parser.collect_all_steps(job.steps)
    assert len(flat_steps) == 4
    
    # Check STEP1
    step1 = flat_steps[0]
    assert step1["name"] == "STEP1"
    assert step1["pgm"] == "COBPROG1"
    assert "INPUTDD" in step1["dds"]
    assert step1["dds"]["INPUTDD"]["dsn"] == "MY.INPUT.DATA"
    assert step1["dds"]["SYSIN"]["sysin_data"] == "SYSIN DATA LINE 1"
    
    # Check PROC expansion on STEP2
    step2 = flat_steps[1]
    assert step2["name"] == "STEP2.PROCSTEP"
    assert step2["pgm"] == "COBPROG2"
    assert "REPORTDD" in step2["dds"]
    assert step2["dds"]["REPORTDD"]["dsn"] == "MY.REPORT.DATA" # Symbol outputfile replaced
    assert len(step2["conds"]) == 1
    assert step2["conds"][0] == (0, "NE", "STEP1")

def test_jcl_parser_invalid():
    jcl_path = r"c:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test\tests\repos\JCLINVALID01\src\JCLINVALID01.jcl"
    content = open(jcl_path, "r", encoding="utf-8").read()
    parser = JclParser(content)
    job = parser.parse()
    
    diags = parser.diagnostics
    assert len(diags) > 0
    
    reasons = [d["reason"] for d in diags]
    # Check that we logged expected syntax/logical errors
    assert any("JCL_INVALID_STEP" in r for r in reasons)
    assert any("JCL_UNRESOLVED_PROC" in r for r in reasons)
    assert any("JCL_UNRESOLVED_SYMBOL" in r for r in reasons)
    assert any("JCL_UNSUPPORTED_CONDITION" in r for r in reasons)
    assert any("UNRESOLVED_DATASET" in r for r in reasons)

def test_jcl_pipeline_e2e():
    repo = r"c:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test\tests\repos\JCLBATCH01"
    out_dir = r"c:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test\target\modernized_test"
    
    # Create input dataset
    input_file = os.path.join(repo, "MY.INPUT.DATA")
    with open(input_file, "w", encoding="utf-8") as f:
        f.write("HELLO WORLD".ljust(80))
        
    try:
        pipeline = NativePipeline(repo, out_dir)
        pipeline.run_legacy_baseline = lambda: None
        
        # Override stage_execute_gate to capture and verify JCL execution
        original_execute_gate = pipeline.stage_execute_gate
        def execute_jcl_job(src):
            # Compile dependencies classpath
            classpath = "target/classes"
            cp_file = os.path.join(pipeline.generated_dir, "cp.txt")
            try:
                mvn_exe = "mvn.cmd" if os.name == "nt" else "mvn"
                subprocess.run([
                    mvn_exe, "-o", "dependency:build-classpath", "-Dmdep.outputFile=cp.txt"
                ], cwd=pipeline.generated_dir, capture_output=True, text=True)
                if os.path.exists(cp_file):
                    with open(cp_file, "r", encoding="utf-8") as fh:
                        cp_deps = fh.read().strip()
                    if cp_deps:
                        classpath += os.pathsep + cp_deps
            except Exception:
                pass
                
            # Run the compiled JCL Job main class
            results_dir = os.path.join(out_dir, "results", "native")
            os.makedirs(results_dir, exist_ok=True)
            tgt_input = os.path.join(results_dir, "MY.INPUT.DATA")
            shutil.copy2(input_file, tgt_input)
            
            res = subprocess.run([
                "java", "-cp", classpath, "com.systema.modernized.native_gen.JclJob_Jclbatch01"
            ], cwd=pipeline.generated_dir, capture_output=True, text=True)
            
            # Print outputs for diagnostics
            print("=== JCL RUN STDOUT ===")
            print(res.stdout)
            print("=== JCL RUN STDERR ===")
            print(res.stderr)
            
            # Assert execution returned successfully
            assert res.returncode == 0
            
            # Verify execution order and bypass logic from logs
            assert "=== START JCL JOB: JCLBATCH01 ===" in res.stdout
            assert "=== EXECUTE STEP: STEP1 (PGM: COBPROG1) ===" in res.stdout
            assert "=== EXECUTE STEP: STEP2.PROCSTEP (PGM: COBPROG2) ===" in res.stdout
            assert "STEP BYPASS: STEPBYPS" in res.stdout
            assert "=== EXECUTE STEP: STEP3 (PGM: COBPROG3) ===" in res.stdout
            assert "=== END JCL JOB: JCLBATCH01 ===" in res.stdout
            
            # Verify data resolution equivalence across steps
            # Target output files: in repo since JclExecutionContext.setDdAssignment resolves them
            output_data = os.path.join(results_dir, "MY.OUTPUT.DATA")
            report_data = os.path.join(results_dir, "MY.REPORT.DATA")
            final_data = os.path.join(results_dir, "MY.FINAL.DATA")
            
            assert os.path.exists(output_data), "MY.OUTPUT.DATA was not created"
            assert os.path.exists(report_data), "MY.REPORT.DATA was not created"
            assert os.path.exists(final_data), "MY.FINAL.DATA was not created"
            
            # Read files and verify output strings
            with open(output_data, "r", encoding="utf-8") as fh:
                out_content = fh.read().strip()
            with open(report_data, "r", encoding="utf-8") as fh:
                rep_content = fh.read().strip()
            with open(final_data, "r", encoding="utf-8") as fh:
                fin_content = fh.read().strip()
                
            assert "PROG1:HELLO WORLD" in out_content
            assert "SYSIN DATA LINE 1" in out_content
            assert "PROG2:" in rep_content
            assert "PROG3:" in fin_content
            
            return True
            
        pipeline.stage_execute_gate = execute_jcl_job
        pipeline.stage_equivalence_gate = lambda selected_src: "PASS"
        pipeline.stage_negative_equivalence = lambda selected_src: True
        
        res = pipeline.run()
        assert res == "NATIVE_JAVA_VERIFIED"
        
    finally:
        if os.path.exists(input_file):
            os.remove(input_file)
        # Cleanup files generated during execution
        for f in ["MY.INPUT.DATA", "MY.OUTPUT.DATA", "MY.REPORT.DATA", "MY.FINAL.DATA"]:
            if os.path.exists(f):
                os.remove(f)
