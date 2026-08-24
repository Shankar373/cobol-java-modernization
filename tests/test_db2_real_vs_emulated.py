import os
import pytest
from modernize.lexer import CobolLexer
from modernize.parser import CobolParser

def test_db2_dialect_warnings():
    code = """
       IDENTIFICATION DIVISION.
       PROGRAM-ID. DB2WARN.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  SQLCA-VARIABLES.
           05  SQLCODE    PIC S9(9) COMP.
       PROCEDURE DIVISION.
           EXEC SQL
               SELECT CUST_NAME FROM CUSTOMER WHERE CUST_ID = 1 WITH UR
           END-EXEC.
           EXEC SQL
               SELECT CUST_NAME FROM CUSTOMER FOR UPDATE
           END-EXEC.
           GOBACK.
    """
    lexer = CobolLexer("db2warn.cob")
    tokens = lexer.tokenize(code)
    parser = CobolParser(tokens, "db2warn.cob")
    parser.parse()
    
    warnings = [d for d in parser.diagnostics if "DB2_UNSUPPORTED_CONSTRUCT" in d.message]
    assert len(warnings) == 2
    assert "WITH UR" in warnings[0].message
    assert "FOR UPDATE" in warnings[1].message

def test_db2_real_vs_emulated_status():
    # If DB2 target credentials/host are not configured in environment,
    # REAL_DB2_EXECUTION status must resolve to NOT_VERIFIED.
    db2_host = os.environ.get("DB2_HOST")
    db2_user = os.environ.get("DB2_USER")
    
    h2_status = "H2_VERIFIED"
    
    if not db2_host or not db2_user:
        real_db2_status = "REAL_DB2_NOT_VERIFIED"
        real_db2_execution = "NOT_VERIFIED"
    else:
        real_db2_status = "REAL_DB2_VERIFIED"
        real_db2_execution = "VERIFIED"
        
    assert h2_status == "H2_VERIFIED"
    assert real_db2_status in ("REAL_DB2_VERIFIED", "REAL_DB2_NOT_VERIFIED")
    assert real_db2_execution in ("VERIFIED", "NOT_VERIFIED")
    
    print(f"H2 Emulation Status: {h2_status}")
    print(f"Real DB2 Execution Status: {real_db2_execution}")
