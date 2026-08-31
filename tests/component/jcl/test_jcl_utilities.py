import os
import json
import shutil
import tempfile
import pytest
from modernize.lexer import CobolLexer
from modernize.parser import CobolParser
from modernize.jcl_parser import JclParser
from modernize.native_pipeline import NativePipeline

def test_iebgener_emulation_e2e():
    # Setup test workspace
    temp_out = tempfile.mkdtemp()
    
    # Create JCLSYMBOL02 repo mimicking IEBGENER step
    repo_dir = os.path.join(temp_out, "JCLUT1")
    os.makedirs(os.path.join(repo_dir, "src"), exist_ok=True)
    
    # Write JCL
    jcl_content = """//JCLUT1 JOB (ACCT),'UTILITY_TEST'
//STEP1   EXEC PGM=IEBGENER
//SYSUT1  DD DSN='MY.INPUT.DATA',DISP=SHR
//SYSUT2  DD DSN='MY.OUTPUT.DATA',DISP=(NEW,CATLG)
//SYSIN   DD DUMMY
"""
    with open(os.path.join(repo_dir, "src", "JCLUT1.jcl"), "w", encoding="utf-8") as fh:
        fh.write(jcl_content)
        
    config = {
        "main_program": "JCLUT1.jcl",
        "file_assignments": {
            "SYSUT1": "MY.INPUT.DATA",
            "SYSUT2": "MY.OUTPUT.DATA"
        }
    }
    with open(os.path.join(repo_dir, "migration_config.json"), "w", encoding="utf-8") as fh:
        json.dump(config, fh)
        
    try:
        # Pre-seed expected baseline stdout.txt
        expected_stdout = (
            "=== START JCL JOB: JCLUT1 ===\n"
            "=== EXECUTE STEP: STEP1 (PGM: IEBGENER) ===\n"
            "=== EXECUTE UTILITY: IEBGENER ===\n"
            "STEP STEP1 FINISHED WITH RC: 0\n"
            "=== END JCL JOB: JCLUT1 ===\n"
        )
        
        baseline_dir = os.path.join(temp_out, "baseline", "legacy")
        os.makedirs(baseline_dir, exist_ok=True)
        with open(os.path.join(baseline_dir, "stdout.txt"), "w", encoding="utf-8") as fh:
            fh.write(expected_stdout)
            
        os.makedirs(os.path.join(temp_out, "results", "native"), exist_ok=True)
        with open(os.path.join(temp_out, "results", "native", "MY.INPUT.DATA"), "w", encoding="utf-8") as fh:
            fh.write("LINE 1\nLINE 2\n")
            
        p = NativePipeline(repo_dir, temp_out)
        p.run_legacy_baseline = lambda: None
        verdict = p.run()
        
        assert verdict == "NATIVE_JAVA_VERIFIED", f"IEBGENER utility pipeline failed: {verdict}"
        
        # Verify copied output
        copied_file = os.path.join(temp_out, "results", "native", "MY.OUTPUT.DATA")
        assert os.path.exists(copied_file)
        with open(copied_file, "r") as fh:
            content = fh.read()
        assert content == "LINE 1\nLINE 2\n"
        
    finally:
        shutil.rmtree(temp_out, ignore_errors=True)

def test_idcams_emulation_e2e():
    temp_out = tempfile.mkdtemp()
    repo_dir = os.path.join(temp_out, "JCLUT2")
    os.makedirs(os.path.join(repo_dir, "src"), exist_ok=True)
    
    jcl_content = """//JCLUT2 JOB (ACCT),'IDCAMS_TEST'
//STEP1   EXEC PGM=IDCAMS
//SYSIN   DD *
  DELETE MY.DEL.DATA
  DEFINE CLUSTER NAME(MY.NEW.CLUSTER)
/*
"""
    with open(os.path.join(repo_dir, "src", "JCLUT2.jcl"), "w", encoding="utf-8") as fh:
        fh.write(jcl_content)
        
    config = {
        "main_program": "JCLUT2.jcl",
        "file_assignments": {}
    }
    with open(os.path.join(repo_dir, "migration_config.json"), "w", encoding="utf-8") as fh:
        json.dump(config, fh)
        
    try:
        expected_stdout = (
            "=== START JCL JOB: JCLUT2 ===\n"
            "=== EXECUTE STEP: STEP1 (PGM: IDCAMS) ===\n"
            "=== EXECUTE UTILITY: IDCAMS ===\n"
            "IDCAMS: Deleted file " + os.path.abspath(os.path.join(temp_out, "results", "native", "MY.DEL.DATA")) + "\n"
            "IDCAMS: Defined cluster (created file) " + os.path.abspath(os.path.join(temp_out, "results", "native", "MY.NEW.CLUSTER")) + "\n"
            "STEP STEP1 FINISHED WITH RC: 0\n"
            "=== END JCL JOB: JCLUT2 ===\n"
        )
        
        baseline_dir = os.path.join(temp_out, "baseline", "legacy")
        os.makedirs(baseline_dir, exist_ok=True)
        with open(os.path.join(baseline_dir, "stdout.txt"), "w", encoding="utf-8") as fh:
            fh.write(expected_stdout)
            
        os.makedirs(os.path.join(temp_out, "results", "native"), exist_ok=True)
        del_file = os.path.join(temp_out, "results", "native", "MY.DEL.DATA")
        with open(del_file, "w") as fh:
            fh.write("to delete")
            
        p = NativePipeline(repo_dir, temp_out)
        p.run_legacy_baseline = lambda: None
        verdict = p.run()
        
        assert verdict == "NATIVE_JAVA_VERIFIED", f"IDCAMS utility pipeline failed: {verdict}"
        
        # Verify cluster created, del file deleted
        assert not os.path.exists(del_file)
        assert os.path.exists(os.path.join(temp_out, "results", "native", "MY.NEW.CLUSTER"))
        
    finally:
        shutil.rmtree(temp_out, ignore_errors=True)

def test_sort_emulation_e2e():
    temp_out = tempfile.mkdtemp()
    repo_dir = os.path.join(temp_out, "JCLUT3")
    os.makedirs(os.path.join(repo_dir, "src"), exist_ok=True)
    
    jcl_content = """//JCLUT3 JOB (ACCT),'SORT_TEST'
//STEP1   EXEC PGM=SORT
//SORTIN  DD DSN='MY.UNSORTED.DATA',DISP=SHR
//SORTOUT DD DSN='MY.SORTED.DATA',DISP=(NEW,CATLG)
//SYSIN   DD *
  SORT FIELDS=(1,4,CH,A)
/*
"""
    with open(os.path.join(repo_dir, "src", "JCLUT3.jcl"), "w", encoding="utf-8") as fh:
        fh.write(jcl_content)
        
    config = {
        "main_program": "JCLUT3.jcl",
        "file_assignments": {
            "SORTIN": "MY.UNSORTED.DATA",
            "SORTOUT": "MY.SORTED.DATA"
        }
    }
    with open(os.path.join(repo_dir, "migration_config.json"), "w", encoding="utf-8") as fh:
        json.dump(config, fh)
        
    try:
        expected_stdout = (
            "=== START JCL JOB: JCLUT3 ===\n"
            "=== EXECUTE STEP: STEP1 (PGM: SORT) ===\n"
            "=== EXECUTE UTILITY: SORT ===\n"
            "STEP STEP1 FINISHED WITH RC: 0\n"
            "=== END JCL JOB: JCLUT3 ===\n"
        )
        
        baseline_dir = os.path.join(temp_out, "baseline", "legacy")
        os.makedirs(baseline_dir, exist_ok=True)
        with open(os.path.join(baseline_dir, "stdout.txt"), "w", encoding="utf-8") as fh:
            fh.write(expected_stdout)
            
        os.makedirs(os.path.join(temp_out, "results", "native"), exist_ok=True)
        with open(os.path.join(temp_out, "results", "native", "MY.UNSORTED.DATA"), "w", encoding="utf-8") as fh:
            fh.write("ZZZZ\nBBBB\nAAAA\nCCCC\n")
            
        p = NativePipeline(repo_dir, temp_out)
        p.run_legacy_baseline = lambda: None
        verdict = p.run()
        
        assert verdict == "NATIVE_JAVA_VERIFIED", f"SORT utility pipeline failed: {verdict}"
        
        # Verify sorted output
        sorted_file = os.path.join(temp_out, "results", "native", "MY.SORTED.DATA")
        assert os.path.exists(sorted_file)
        with open(sorted_file, "r") as fh:
            content = fh.read()
        assert content == "AAAA\nBBBB\nCCCC\nZZZZ\n"
        
    finally:
        shutil.rmtree(temp_out, ignore_errors=True)
