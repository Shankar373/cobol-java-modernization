import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modernize.native_generator import NativeStatementTranslator

def test_translate_move():
    var_types = {"VAR-A": "String", "VAR-B": "String", "VAR-C": "BigDecimal"}
    trans = NativeStatementTranslator(var_types)
    
    node_move = {
        "properties": {
            "statement_type": "MOVE",
            "source": "VAR-A",
            "target": "VAR-B"
        }
    }
    java_code = trans.translate_statement(node_move)
    assert java_code == "var_b = var_a;"

    node_move_literal = {
        "properties": {
            "statement_type": "MOVE",
            "source": "100.50",
            "target": "VAR-C"
        }
    }
    java_code_literal = trans.translate_statement(node_move_literal)
    assert java_code_literal == 'var_c = new BigDecimal("100.50");'

def test_translate_arithmetic():
    var_types = {"VAR-X": "BigDecimal", "VAR-Y": "BigDecimal"}
    trans = NativeStatementTranslator(var_types)
    
    node_add = {
        "properties": {
            "statement_type": "ADD",
            "value": "10.00",
            "target": "VAR-X"
        }
    }
    java_add = trans.translate_statement(node_add)
    assert java_add == 'var_x = var_x.add(new BigDecimal("10.00"));'

def test_translate_display():
    var_types = {"VAR-A": "String", "VAR-B": "BigDecimal"}
    trans = NativeStatementTranslator(var_types)
    
    node_display = {
        "properties": {
            "statement_type": "DISPLAY",
            "operands": [
                {"type": "literal", "value": "Total: "},
                {"type": "variable", "value": "VAR-A"},
                {"type": "variable", "value": "VAR-B"}
            ]
        }
    }
    java_display = trans.translate_statement(node_display)
    assert java_display == 'System.out.println("Total: " + " " + var_a + " " + String.valueOf(var_b));'


def test_translate_move_function_numval():
    var_types = {"TX-AMOUNT-TEXT": "String", "TX-AMOUNT": "BigDecimal"}
    trans = NativeStatementTranslator(var_types)
    node_move = {
        "properties": {
            "statement_type": "MOVE",
            "source": "FUNCTION NUMVAL(TX-AMOUNT-TEXT)",
            "targets": ["TX-AMOUNT"]
        }
    }
    java_code = trans.translate_statement(node_move)
    assert java_code == "tx_amount = com.systema.modernized.CobolFormatHelper.numval(tx_amount_text);"


def test_translate_spaces_condition():
    var_types = {"TX-AMOUNT-TEXT": "String"}
    trans = NativeStatementTranslator(var_types)
    cond = trans._translate_condition("TX-AMOUNT-TEXT NOT = SPACES")
    assert cond == "!tx_amount_text.equals(\"\")"


def test_translate_function_mod():
    var_types = {"WS-YEAR": "Integer", "WS-RESULT": "Integer"}
    trans = NativeStatementTranslator(var_types)
    node_move = {
        "properties": {
            "statement_type": "MOVE",
            "source": "FUNCTION MOD(WS-YEAR, 4)",
            "targets": ["WS-RESULT"]
        }
    }
    java_code = trans.translate_statement(node_move)
    assert java_code == "ws_result = (com.systema.modernized.CobolFormatHelper.mod(BigDecimal.valueOf(ws_year), new BigDecimal(\"4\"))).intValue();"


def test_translate_condition_function_mod():
    var_types = {"WS-YEAR": "Integer"}
    trans = NativeStatementTranslator(var_types)
    cond = trans._translate_condition("FUNCTION MOD(WS-YEAR, 4) = 0")
    assert cond == "com.systema.modernized.CobolFormatHelper.mod(ws_year, 4) == 0"


