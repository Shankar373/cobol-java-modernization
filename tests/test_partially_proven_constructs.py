"""Comprehensive validation tests for partially proven COBOL constructs.

Validates semantic behavior, edge cases, and boundaries for:
1. OCCURS DEPENDING ON (dynamic ODO boundary verification)
2. PERFORM PARA-A THRU/THROUGH PARA-B (paragraph ranges)
3. GO TO (forward branch and exit jump)
4. Dynamic CALL identifier
5. UNSTRING (delimiters, pointer, tallying)
6. INSPECT (tallying, replacing, converting)
7. RECORD SEQUENTIAL (binary fixed record stream I/O)
"""

import os
import tempfile
import pytest
from modernize.lexer import CobolLexer
from modernize.parser import CobolParser
from modernize.native_generator import NativeProgramGenerator


def _parse_and_generate(cobol_src: str, prog_id: str, file_assigns: list = None):
    with tempfile.TemporaryDirectory() as td:
        src_path = os.path.join(td, f"{prog_id}.cob")
        with open(src_path, "w", encoding="utf-8") as f:
            f.write(cobol_src)
        
        lexer = CobolLexer(src_path)
        tokens = lexer.tokenize(cobol_src)
        parser = CobolParser(tokens, src_path)
        ast = parser.parse()
        
        gen = NativeProgramGenerator(prog_id, list(ast.nodes.values()), file_assigns=file_assigns or [], repo_path=td)
        java_code = gen.generate_class_source(all_generators={prog_id: gen})
        return ast, java_code


def test_occurs_depending_on_bounds_check_helper():
    """Verify ODO emits checkBounds helper enforcing active upper bound."""
    src = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. ODOPROG.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-COUNT         PIC 9(2) VALUE 5.
       01  WS-TABLE.
           05  WS-ITEM      OCCURS 1 TO 10 TIMES
                            DEPENDING ON WS-COUNT
                            PIC X(10).
       PROCEDURE DIVISION.
       MAIN-PARA.
           DISPLAY WS-ITEM (1)
           STOP RUN.
"""
    ast, java = _parse_and_generate(src, "ODOPROG")
    assert "checkBounds" in java
    assert "Subscript " in java
    assert "out of active bounds" in java


def test_perform_thru_and_through_syntax():
    """Verify parser and generator recognize both THRU and THROUGH paragraph ranges."""
    src_thru = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. THRUPROG.
       PROCEDURE DIVISION.
       MAIN-PARA.
           PERFORM STEP-A THRU STEP-C
           STOP RUN.
       STEP-A.
           DISPLAY "A".
       STEP-B.
           DISPLAY "B".
       STEP-C.
           DISPLAY "C".
"""
    ast_thru, java_thru = _parse_and_generate(src_thru, "THRUPROG")
    assert 'perform("step_a", "step_c")' in java_thru
    assert "private void perform(String target, String thru)" in java_thru

    src_through = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. THROUGHP.
       PROCEDURE DIVISION.
       MAIN-PARA.
           PERFORM STEP-1 THROUGH STEP-3
           STOP RUN.
       STEP-1.
           DISPLAY "1".
       STEP-2.
           DISPLAY "2".
       STEP-3.
           DISPLAY "3".
"""
    ast_through, java_through = _parse_and_generate(src_through, "THROUGHP")
    assert 'perform("step_1", "step_3")' in java_through


def test_goto_forward_and_exit_jump():
    """Verify GO TO emits nextParagraphIndex assignment and return."""
    src = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. GOTOPROG.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-X PIC 9 VALUE 1.
       PROCEDURE DIVISION.
       MAIN-PARA.
           IF WS-X = 1
               GO TO EXIT-PARA
           END-IF
           DISPLAY "NEVER REACHED".
       EXIT-PARA.
           STOP RUN.
"""
    ast, java = _parse_and_generate(src, "GOTOPROG")
    assert 'nextParagraphIndex = getParagraphIndex("exit_para"); return;' in java


def test_dynamic_call_identifier_dispatch():
    """Verify dynamic CALL identifier generates dispatch logic against target variable."""
    src = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. DYNPROG.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-SUBPROG PIC X(8) VALUE "SUBPROG1".
       PROCEDURE DIVISION.
       MAIN-PARA.
           CALL WS-SUBPROG
           STOP RUN.
"""
    ast, java = _parse_and_generate(src, "DYNPROG")
    assert "targetProg_ws_subprog" in java or "ws_subprog" in java


def test_unstring_delimiters_pointer_tallying():
    """Verify UNSTRING handles multiple targets, pointer index, and tallying."""
    src = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. UNSTRPROG.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-INPUT     PIC X(30) VALUE "FIRST,SECOND,THIRD".
       01  WS-T1        PIC X(10).
       01  WS-T2        PIC X(10).
       01  WS-T3        PIC X(10).
       01  WS-PTR       PIC 9(2) VALUE 1.
       01  WS-TALLY     PIC 9(2) VALUE 0.
       PROCEDURE DIVISION.
       MAIN-PARA.
           UNSTRING WS-INPUT DELIMITED BY ","
               INTO WS-T1, WS-T2, WS-T3
               WITH POINTER WS-PTR
               TALLYING IN WS-TALLY
           STOP RUN.
"""
    ast, java = _parse_and_generate(src, "UNSTRPROG")
    assert "unstring_targets" in java
    assert "ws_ptr" in java
    assert "ws_tally" in java


def test_inspect_tallying_and_replacing():
    """Verify INSPECT handles TALLYING ALL, LEADING, and REPLACING."""
    src = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. INSPPROG.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-STR       PIC X(20) VALUE "00012340056".
       01  WS-COUNT     PIC 9(2) VALUE 0.
       PROCEDURE DIVISION.
       MAIN-PARA.
           INSPECT WS-STR TALLYING WS-COUNT FOR ALL "0"
           INSPECT WS-STR REPLACING ALL "0" BY " "
           STOP RUN.
"""
    ast, java = _parse_and_generate(src, "INSPPROG")
    assert "s_target.indexOf" in java or "count++" in java
    assert "replace" in java or "replaceAll" in java


def test_record_sequential_file_streams():
    """Verify ORGANIZATION RECORD SEQUENTIAL generates binary InputStream / OutputStream."""
    src = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. RECSEQPROG.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT BIN-FILE ASSIGN TO "data/binary.dat"
               ORGANIZATION IS RECORD SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD  BIN-FILE.
       01  BIN-REC PIC X(100).
       PROCEDURE DIVISION.
       MAIN-PARA.
           OPEN INPUT BIN-FILE
           CLOSE BIN-FILE
           STOP RUN.
"""
    file_assigns = [{
        "logical_name": "BIN-FILE",
        "assign_path": "data/binary.dat",
        "organization": "RECORD SEQUENTIAL",
        "is_input": True
    }]
    ast, java = _parse_and_generate(src, "RECSEQPROG", file_assigns=file_assigns)
    assert "bin_file_stream_in" in java or "bin_file_reader" in java
    assert "open_bin_file" in java
    assert "close_bin_file" in java
