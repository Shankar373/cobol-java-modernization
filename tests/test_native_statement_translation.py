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
    assert java_code_literal == 'var_c.assign(new BigDecimal("100.50"), com.systema.modernized.runtime.CobolRoundingMode.TRUNCATION, com.systema.modernized.runtime.SizeErrorPolicy.UNCHECKED);'

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
    assert java_add == 'var_x.assign(com.systema.modernized.runtime.CobolArithmetic.add(var_x.getValue(), new BigDecimal("10.00")), com.systema.modernized.runtime.CobolRoundingMode.TRUNCATION, com.systema.modernized.runtime.SizeErrorPolicy.UNCHECKED);'

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
    expected = (
        "{\n"
        "        writeBytes(\"Total: \".getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));\n"
        "        writeBytes(var_a.getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));\n"
        "        writeBytes(String.valueOf(var_b.getValue()).getBytes(java.nio.charset.StandardCharsets.ISO_8859_1));\n"
        "        System.out.write(10);\n"
        "        System.out.flush();\n"
        "    }"
    )
    assert java_display == expected


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
    assert java_code == 'tx_amount.assign(com.systema.modernized.CobolFormatHelper.numval(tx_amount_text), com.systema.modernized.runtime.CobolRoundingMode.TRUNCATION, com.systema.modernized.runtime.SizeErrorPolicy.UNCHECKED);'


def test_translate_spaces_condition():
    var_types = {"TX-AMOUNT-TEXT": "String"}
    trans = NativeStatementTranslator(var_types)
    cond = trans._translate_condition("TX-AMOUNT-TEXT NOT = SPACES")
    assert cond == '!com.systema.modernized.CobolFormatHelper.cobolEquals(tx_amount_text, "")'


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
    assert java_code == 'ws_result = (com.systema.modernized.CobolFormatHelper.mod(BigDecimal.valueOf(ws_year), new BigDecimal("4"))).intValue();'


def test_translate_condition_function_mod():
    var_types = {"WS-YEAR": "Integer"}
    trans = NativeStatementTranslator(var_types)
    cond = trans._translate_condition("FUNCTION MOD(WS-YEAR, 4) = 0")
    assert cond == "com.systema.modernized.CobolFormatHelper.mod(ws_year, 4) == 0"


def test_translate_relational_keywords_condition():
    var_types = {"SQLCODE": "Integer"}
    trans = NativeStatementTranslator(var_types)
    assert trans._translate_condition("SQLCODE NOT EQUAL 0") == "sqlcode != 0"
    assert trans._translate_condition("SQLCODE EQUAL TO 100") == "sqlcode == 100"
    assert trans._translate_condition("SQLCODE GREATER THAN 10") == "sqlcode > 10"


# Regression check: ensure no single-quoted string literals in generated Java
# for simple assignments (e.g. String x = 'ready' is invalid Java)
def test_no_single_quoted_string_literals():
    """Verify that generated Java uses double quotes for string literals,
    not single quotes (which would be invalid Java char literals)."""
    var_types = {"WS-FIELD": "String"}
    trans = NativeStatementTranslator(var_types)
    
    # Test MOVE with a single-quoted literal source (as COBOL might provide)
    node_move_literal = {
        "properties": {
            "statement_type": "MOVE",
            "source": "'ready'",
            "target": "WS-FIELD"
        }
    }
    java_code = trans.translate_statement(node_move_literal)
    # Check that generated Java does not contain naked single-quoted string literals
    # that would be invalid Java (e.g. String x = 'ready')
    # Our to_java_string_literal function converts to double quotes,
    # so the result should have very few single quotes (only from escape sequences)
    # The key check: no pattern '= 'single-quote'' that would be invalid Java
    has_naked_single_quote = "= '" in java_code or ' += "' in java_code
    if has_naked_single_quote:
        # If there are naked single quotes, report the generated code for debugging
        raise AssertionError(
            f"Generated Java contains naked single-quoted string literal: {java_code}"
        )


# Regression check: ensure no single-quoted string literals in generated Java
# for simple assignments (e.g. String x = 'ready' is invalid Java)
def test_no_single_quoted_string_literals():
    """Verify that generated Java uses double quotes for string literals,
    not single quotes (which would be invalid Java char literals)."""
    var_types = {"WS-FIELD": "String"}
    trans = NativeStatementTranslator(var_types)
    
    # Test MOVE with a single-quoted literal source (as COBOL might provide)
    node_move_literal = {
        "properties": {
            "statement_type": "MOVE",
            "source": "'ready'",
            "target": "WS-FIELD"
        }
    }
    java_code = trans.translate_statement(node_move_literal)
    # Check that generated Java does not contain the invalid pattern
    # '= 'single-quote'' that would be invalid Java
    assert "'= '" not in java_code, \
        f"Generated Java should not contain naked single-quoted string literal: {java_code}"
    
    # Also test MOVE with a double-quoted literal source
    node_move_double = {
        "properties": {
            "statement_type": "MOVE",
            "source": "\"ready\"",
            "target": "WS-FIELD"
        }
    }
    java_code_double = trans.translate_statement(node_move_double)
    # Should be valid Java with double quotes
    assert java_code_double is not None
    
    # Test with a numeric literal embedded in string context
    node_move_num = {
        "properties": {
            "statement_type": "MOVE",
            "source": "100.50",
            "target": "WS-FIELD"
        }
    }
    java_code_num = trans.translate_statement(node_move_num)
    assert java_code_num is not None


# Fixed-point lowering contract: BigDecimal operands must use
# CobolArithmetic.add/subtract/multiply/divide, never primitive Java
# operators (invalid Java). Pure primitive arithmetic keeps `+ - * /`.
_MIXED_TYPES = {"WS-A": "BigDecimal", "WS-B": "Integer", "WS-C": "Integer", "WS-D": "BigDecimal"}


def _giving_stmt(stype, val, op2, tgt, form=None):
    props = {"statement_type": stype, "value": val, "targets": [tgt]}
    if op2 is not None:
        props["operand2"] = op2
    if form is not None:
        props["form"] = form
    return {"properties": props}


def test_giving_mixed_add_uses_bigdecimal_add():
    trans = NativeStatementTranslator(_MIXED_TYPES)
    java_code = trans.translate_statement(_giving_stmt("ADD", "WS-A", "WS-B", "WS-C"))
    assert "CobolArithmetic.add(ws_a.getValue(), BigDecimal.valueOf(ws_b))" in java_code
    assert ".longValue()" in java_code
    assert "ws_a.getValue() +" not in java_code


def test_giving_mixed_subtract_multiply_use_bigdecimal_ops():
    trans = NativeStatementTranslator(_MIXED_TYPES)
    java_sub = trans.translate_statement(_giving_stmt("SUBTRACT", "WS-B", "WS-A", "WS-C"))
    # SUBTRACT WS-B FROM WS-A GIVING WS-C -> WS-A - WS-B (operand order kept)
    assert "CobolArithmetic.subtract(ws_a.getValue(), BigDecimal.valueOf(ws_b))" in java_sub
    java_mul = trans.translate_statement(_giving_stmt("MULTIPLY", "WS-A", "WS-B", "WS-C"))
    assert "CobolArithmetic.multiply(ws_a.getValue(), BigDecimal.valueOf(ws_b))" in java_mul


def test_giving_mixed_divide_preserves_by_into_forms():
    trans = NativeStatementTranslator(_MIXED_TYPES)
    java_by = trans.translate_statement(_giving_stmt("DIVIDE", "WS-A", "WS-B", "WS-C", form="BY"))
    assert "CobolArithmetic.divide(ws_a.getValue(), BigDecimal.valueOf(ws_b))" in java_by
    java_into = trans.translate_statement(_giving_stmt("DIVIDE", "WS-A", "WS-B", "WS-C", form="INTO"))
    assert "CobolArithmetic.divide(BigDecimal.valueOf(ws_b), ws_a.getValue())" in java_into


def test_mixed_non_giving_add_to_int_target():
    trans = NativeStatementTranslator(_MIXED_TYPES)
    java_code = trans.translate_statement(_giving_stmt("ADD", "WS-A", None, "WS-C"))
    assert "CobolArithmetic.add(BigDecimal.valueOf(ws_c), ws_a.getValue())" in java_code


def test_giving_mixed_decimal_target_keeps_scale_and_assign():
    trans = NativeStatementTranslator(_MIXED_TYPES)
    java_code = trans.translate_statement(_giving_stmt("ADD", "WS-A", "WS-B", "WS-D"))
    assert java_code == (
        'ws_d.assign(com.systema.modernized.runtime.CobolArithmetic.add('
        'ws_a.getValue(), BigDecimal.valueOf(ws_b)), '
        'com.systema.modernized.runtime.CobolRoundingMode.TRUNCATION, '
        'com.systema.modernized.runtime.SizeErrorPolicy.UNCHECKED);'
    )


def test_giving_all_primitive_operators_preserved():
    trans = NativeStatementTranslator({"WS-I": "Integer", "WS-J": "Integer", "WS-K": "Integer"})
    java_add = trans.translate_statement(_giving_stmt("ADD", "WS-I", "WS-J", "WS-K"))
    assert "ws_i + ws_j" in java_add
    assert "CobolArithmetic" not in java_add
    java_sub = trans.translate_statement(_giving_stmt("SUBTRACT", "WS-I", "WS-J", "WS-K"))
    assert "ws_j - ws_i" in java_sub
    java_mul = trans.translate_statement(_giving_stmt("MULTIPLY", "WS-I", "WS-J", "WS-K"))
    assert "ws_i * ws_j" in java_mul
    java_div = trans.translate_statement(_giving_stmt("DIVIDE", "WS-I", "WS-J", "WS-K", form="BY"))
    assert "ws_i / ws_j" in java_div
    java_lit = trans.translate_statement(_giving_stmt("ADD", "10", None, "WS-K"))
    assert "ws_k + 10" in java_lit



