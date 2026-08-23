import sys
import os
import subprocess
import tempfile
import shutil
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modernize.lexer import CobolLexer
from modernize.parser import CobolParser
from modernize.native_generator import NativeProgramGenerator

def test_layout01_compilation_and_execution():
    cob_path = "tests/repos/LAYOUT01/LAYOUT01.cob"
    assert os.path.exists(cob_path)
    
    with open(cob_path, "r", encoding="utf-8") as fh:
        code = fh.read()
        
    lexer = CobolLexer(cob_path)
    tokens = lexer.tokenize(code)
    parser = CobolParser(tokens, cob_path)
    ir = parser.parse()
    
    gen = NativeProgramGenerator("LAYOUT01", list(ir.nodes.values()))
    java_source = gen.generate_class_source()
    
    temp_dir = tempfile.mkdtemp()
    try:
        pkg_dir = os.path.join(temp_dir, "com", "systema", "modernized", "native_gen")
        os.makedirs(pkg_dir, exist_ok=True)
        
        src_file = os.path.join(pkg_dir, "Layout01.java")
        with open(src_file, "w", encoding="utf-8") as f:
            f.write(java_source)
            
        compile_res = subprocess.run(
            ["javac", src_file],
            capture_output=True,
            text=True
        )
        if compile_res.returncode != 0:
            raise Exception(f"Java compilation failed:\n{compile_res.stderr}\nSource:\n{java_source}")
            
        run_res = subprocess.run(
            ["java", "-cp", temp_dir, "com.systema.modernized.native_gen.Layout01"],
            capture_output=True,
            text=True
        )
        assert run_res.returncode == 0, f"Run failed:\n{run_res.stderr}"
        lines = [l.strip() for l in run_res.stdout.strip().splitlines()]
        
        # Verify printed outputs
        assert "INITIAL TEXT:  AAAA" in lines
        assert "AFTER NUM MOVE TEXT:  1234" in lines
        assert "AFTER NUM MOVE NUM:  1234" in lines
        assert "ITEM 1:  XYZ" in lines
        assert "ITEM 2:  ABC" in lines
        assert "ITEM 3:  DEF" in lines
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
