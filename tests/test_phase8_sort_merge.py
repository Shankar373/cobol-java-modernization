import os
import json
import shutil
import tempfile
import pytest
from modernize.lexer import CobolLexer
from modernize.parser import CobolParser
from modernize.native_pipeline import NativePipeline

def test_sort_merge_parser():
    src = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. SMTEST.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT SORTWORK ASSIGN TO "sortwork".
       DATA DIVISION.
       FILE SECTION.
       SD  SORTWORK.
       01  WORK-REC.
           05  WORK-KEY PIC 9(2).
       PROCEDURE DIVISION.
           SORT SORTWORK ON ASCENDING KEY WORK-KEY
               USING INFILE GIVING OUTFILE.
           GOBACK.
    """
    lexer = CobolLexer("dummy.cob", format_mode="free")
    tokens = lexer.tokenize(src)
    parser = CobolParser(tokens, "dummy.cob")
    ir = parser.parse()
    
    nodes = list(ir.nodes.values())
    sort_nodes = [n for n in nodes if n.kind == "STATEMENT" and n.properties.get("statement_type") == "SORT"]
    assert len(sort_nodes) == 1
    properties = sort_nodes[0].properties
    assert properties["work_file"] == "SORTWORK"
    assert properties["keys"] == [{"name": "WORK-KEY", "order": "ASCENDING"}]

def test_sort_merge_e2e():
    repo_dir = os.path.join("tests", "repos", "SORTMERGE01")
    temp_out = tempfile.mkdtemp()
    
    input_data = (
        "Alice     30\n"
        "Bob       25\n"
        "Charlie   35\n"
    )
    expected_output = (
        "Bob       25\n"
        "Alice     30\n"
        "Charlie   35\n"
    )
    
    try:
        # Create execution sub-directory results/native
        native_dir = os.path.join(temp_out, "results", "native")
        os.makedirs(native_dir, exist_ok=True)
        
        # Build baseline legacy folder
        baseline_dir = os.path.join(temp_out, "baseline", "legacy")
        os.makedirs(baseline_dir, exist_ok=True)
        
        # For legacy baseline, write expected output.txt
        with open(os.path.join(baseline_dir, "output.txt"), "w", encoding="utf-8") as fh:
            fh.write(expected_output)
            
        # Write input.txt to the native execution directory
        with open(os.path.join(native_dir, "input.txt"), "w", encoding="utf-8") as fh:
            fh.write(input_data)
            
        p = NativePipeline(repo_dir, temp_out)
        verdict = p.run()
        
        # Let's assert output.txt in native execution directory matches expected_output
        out_file = os.path.join(native_dir, "output.txt")
        assert os.path.exists(out_file), f"output.txt was not generated at {out_file}"
        with open(out_file, "r", encoding="utf-8") as fh:
            observed_output = fh.read()
            
        print("=== OBSERVED OUTPUT ===")
        print(repr(observed_output))
        
        assert observed_output.replace("\r\n", "\n") == expected_output.replace("\r\n", "\n")
        assert verdict == "NATIVE_JAVA_VERIFIED", f"Pipeline failed. Check temp out: {temp_out}"
        
    finally:
        shutil.rmtree(temp_out, ignore_errors=True)
