import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modernize.lexer import CobolLexer
from modernize.parser import CobolParser
from modernize.native_generator import NativeProgramGenerator

def test_pic_v_implied_decimal_in_string_statement():
    cobol_src = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. PICVSTRING.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-BALANCE       PIC 9(7)V99 VALUE 0.
       01 WS-ID            PIC 9(6) VALUE 100101.
       01 WS-STATUS        PIC X(10) VALUE "ACTIVE".
       01 WS-LINE          PIC X(80) VALUE SPACES.
       PROCEDURE DIVISION.
           MOVE 100.25 TO WS-BALANCE.
           STRING WS-ID DELIMITED BY SIZE
                  " | " DELIMITED BY SIZE
                  WS-STATUS DELIMITED BY SIZE
                  " | " DELIMITED BY SIZE
                  WS-BALANCE DELIMITED BY SIZE
                  INTO WS-LINE
           END-STRING.
           DISPLAY WS-LINE.
           GOBACK.
"""
    lexer = CobolLexer("PICVSTRING.cob")
    tokens = lexer.tokenize(cobol_src)
    parser = CobolParser(tokens, "PICVSTRING.cob")
    ast = parser.parse()
    
    gen = NativeProgramGenerator("PICVSTRING", list(ast.nodes.values()))
    java_code = gen.generate_class_source()
    
    # Assert that WS-BALANCE in STRING statement generates storage image (000010025) and NOT String.valueOf(ws_balance) which gives 0000100.25
    assert "ws_balance.toStorageImage()" in java_code
    assert "String.valueOf(ws_balance)" not in java_code

def test_pic_v_display_preserves_display_format():
    cobol_src = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. PICVDISP.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-BALANCE       PIC 9(7)V99 VALUE 100.25.
       01 WS-SIGNED-BAL    PIC S9(7)V99 VALUE -50.75.
       PROCEDURE DIVISION.
           DISPLAY WS-BALANCE.
           DISPLAY WS-SIGNED-BAL.
           GOBACK.
"""
    lexer = CobolLexer("PICVDISP.cob")
    tokens = lexer.tokenize(cobol_src)
    parser = CobolParser(tokens, "PICVDISP.cob")
    ast = parser.parse()
    
    gen = NativeProgramGenerator("PICVDISP", list(ast.nodes.values()))
    java_code = gen.generate_class_source()
    
    # DISPLAY continues to use toDisplayString() / formatted display representation
    assert "toDisplayString()" in java_code

def test_pic_v_comp3_in_string_statement():
    cobol_src = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. PICVCOMP3.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-AMOUNT        PIC S9(7)V99 COMP-3 VALUE 0.
       01 WS-OUT           PIC X(30) VALUE SPACES.
       PROCEDURE DIVISION.
           MOVE 123.45 TO WS-AMOUNT.
           STRING WS-AMOUNT DELIMITED BY SIZE
                  INTO WS-OUT
           END-STRING.
           DISPLAY WS-OUT.
           GOBACK.
"""
    lexer = CobolLexer("PICVCOMP3.cob")
    tokens = lexer.tokenize(cobol_src)
    parser = CobolParser(tokens, "PICVCOMP3.cob")
    ast = parser.parse()
    
    gen = NativeProgramGenerator("PICVCOMP3", list(ast.nodes.values()))
    java_code = gen.generate_class_source()
    
    assert "ws_amount.toStorageImage()" in java_code
    assert "String.valueOf(ws_amount)" not in java_code
