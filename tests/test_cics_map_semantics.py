import os
import json
import shutil
import tempfile
import pytest
from modernize.native_pipeline import NativePipeline

def test_cics_map_semantics_options_e2e():
    temp_out = tempfile.mkdtemp()
    repo_dir = os.path.join(temp_out, "CICSMAP01")
    os.makedirs(os.path.join(repo_dir, "src"), exist_ok=True)
    
    # Write a simple COBOL CICS program that sends and receives map with options
    cobol_src = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. COBPROG1.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  MAP-DATA PIC X(10).
       PROCEDURE DIVISION.
           EXEC CICS SEND MAP('MAP1') MAPSET('MSET1')
                     FROM(MAP-DATA) DATAONLY ERASE ALARM FREEKB
           END-EXEC.
           EXEC CICS RECEIVE MAP('MAP1') MAPSET('MSET1')
                     INTO(MAP-DATA)
           END-EXEC.
           GOBACK.
    """
    with open(os.path.join(repo_dir, "src", "COBPROG1.cob"), "w", encoding="utf-8") as fh:
        fh.write(cobol_src)
        
    config = {
        "main_program": "COBPROG1.cob",
        "file_assignments": {}
    }
    with open(os.path.join(repo_dir, "migration_config.json"), "w", encoding="utf-8") as fh:
        json.dump(config, fh)
        
    try:
        # Pre-seed expected baseline stdout.txt
        expected_stdout = (
            "CICS SEND MAP: MAP1 MAPSET: MSET1 DATA:            OPTIONS: {erase=true, freekb=true, alarm=true, dataonly=true}\n"
            "CICS RECEIVE MAP: MAP1 MAPSET: MSET1 OPTIONS: {}\n"
        )
        
        baseline_dir = os.path.join(temp_out, "baseline", "legacy")
        os.makedirs(baseline_dir, exist_ok=True)
        with open(os.path.join(baseline_dir, "stdout.txt"), "w", encoding="utf-8") as fh:
            fh.write(expected_stdout)
            
        p = NativePipeline(repo_dir, temp_out)
        p.run_legacy_baseline = lambda: None
        verdict = p.run()
        
        assert verdict == "NATIVE_JAVA_VERIFIED", f"CICS map semantics options pipeline failed: {verdict}"
        
    finally:
        shutil.rmtree(temp_out, ignore_errors=True)
