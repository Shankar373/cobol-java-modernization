import os
import shutil
import tempfile
import pytest
import subprocess
from modernize.lexer import CobolLexer
from modernize.parser import CobolParser
from modernize.native_pipeline import NativePipeline

def test_cics_lexer():
    src = "       EXEC CICS SEND MAP('OUTMAP') END-EXEC."
    lexer = CobolLexer("dummy.cob", format_mode="free")
    tokens = lexer.tokenize(src)
    cics_toks = [t for t in tokens if t.type == "EXEC_CICS"]
    assert len(cics_toks) == 1
    assert "SEND MAP('OUTMAP')" in cics_toks[0].value

def test_cics_parser_valid():
    src = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. TESTCICS.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-VAR PIC X(10).
       PROCEDURE DIVISION.
           EXEC CICS SEND MAP('MAP1') FROM(WS-VAR) END-EXEC.
    """
    lexer = CobolLexer("dummy.cob", format_mode="free")
    tokens = lexer.tokenize(src)
    parser = CobolParser(tokens, "dummy.cob")
    ir = parser.parse()
    # Find statements
    cics_nodes = [n for n in ir.nodes.values() if n.kind == "STATEMENT" and n.properties.get("statement_type") == "EXEC_CICS"]
    assert len(cics_nodes) == 1
    assert cics_nodes[0].properties["cics_props"]["cics_type"] == "SEND"

def test_cics_pipeline_e2e():
    repo = r"c:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test\tests\repos\CICSREST01"
    out_dir = tempfile.mkdtemp()
    try:
        pipeline = NativePipeline(repo, out_dir)
        pipeline.run_legacy_baseline = lambda: None
        
        # Override to verify program runs with LINK arg
        original_execute_gate = pipeline.stage_execute_gate
        def execute_with_args(src):
            prog_id = os.path.splitext(os.path.basename(src))[0]
            if prog_id.upper() == "CICSREST01":
                # Execute standalone Maven compilation
                # Build classpath
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
                
                # Execute Cicsrest01 with "LINK" argument
                res = subprocess.run([
                    "java", "-cp", classpath, "com.systema.modernized.native_gen.Cicsrest01", "LINK"
                ], cwd=pipeline.generated_dir, capture_output=True, text=True)
                
                # Debug output helper
                def print_debug():
                    print("=== JAVA PROCESS STDOUT ===")
                    print(res.stdout)
                    print("=== JAVA PROCESS STDERR ===")
                    print(res.stderr)
                    
                    registry_path = os.path.join(pipeline.generated_dir, "src/main/java/com/systema/modernized/CicsProgramRegistry.java")
                    if os.path.exists(registry_path):
                        print("=== CicsProgramRegistry.java ===")
                        with open(registry_path, "r", encoding="utf-8") as f:
                            print(f.read())
                            
                    cicsrest_path = os.path.join(pipeline.generated_dir, "src/main/java/com/systema/modernized/native_gen/Cicsrest01.java")
                    if os.path.exists(cicsrest_path):
                        print("=== Cicsrest01.java ===")
                        with open(cicsrest_path, "r", encoding="utf-8") as f:
                            print(f.read())
                            
                    linkprog_path = os.path.join(pipeline.generated_dir, "src/main/java/com/systema/modernized/native_gen/Linkprog.java")
                    if os.path.exists(linkprog_path):
                        print("=== Linkprog.java ===")
                        with open(linkprog_path, "r", encoding="utf-8") as f:
                            print(f.read())

                if res.returncode != 0:
                    print_debug()
                assert res.returncode == 0
                
                import re
                if not re.search(r"RECEIVED INPUT:\s*LINK", res.stdout):
                    print_debug()
                    assert False, "RECEIVED INPUT: LINK not found in stdout"
                    
                if "LINKPROG CALLED" not in res.stdout:
                    print_debug()
                    assert False, "LINKPROG CALLED not found in stdout"
                    
                if not re.search(r"LINK COMMAREA:\s*UPDATEDVAL", res.stdout):
                    print_debug()
                    assert False, "LINK COMMAREA: UPDATEDVAL not found in stdout"
                
                # Execute Cicsrest01 with "XCTL" argument
                res2 = subprocess.run([
                    "java", "-cp", classpath, "com.systema.modernized.native_gen.Cicsrest01", "XCTL"
                ], cwd=pipeline.generated_dir, capture_output=True, text=True)
                if res2.returncode != 0:
                    print("=== XCTL PROCESS STDOUT ===")
                    print(res2.stdout)
                    print("=== XCTL PROCESS STDERR ===")
                    print(res2.stderr)
                assert res2.returncode == 0
                
                if not re.search(r"RECEIVED INPUT:\s*XCTL", res2.stdout):
                    assert False, "RECEIVED INPUT: XCTL not found in stdout"
                    
                if "LINKPROG CALLED" not in res2.stdout:
                    assert False, "LINKPROG CALLED not found in stdout"
                
            return original_execute_gate(src)
            
        pipeline.stage_execute_gate = execute_with_args
        pipeline.stage_equivalence_gate = lambda selected_src: "PASS"
        pipeline.stage_negative_equivalence = lambda selected_src: True
        
        res = pipeline.run()
        assert res == "NATIVE_JAVA_VERIFIED"
    finally:
        shutil.rmtree(out_dir, ignore_errors=True)

def test_cics_parser_invalid_variable():
    src = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. TESTCICS.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       PROCEDURE DIVISION.
           EXEC CICS SEND MAP('MAP1') FROM(UNDECLARED-VAR) END-EXEC.
    """
    lexer = CobolLexer("dummy.cob", format_mode="free")
    tokens = lexer.tokenize(src)
    parser = CobolParser(tokens, "dummy.cob")
    parser.parse()
    assert len(parser.diagnostics) > 0
    assert "CICS_HOST_VARIABLE_NOT_FOUND" in str(parser.diagnostics[0])


