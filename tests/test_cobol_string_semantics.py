import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modernize.native_generator import NativeStatementTranslator, NativeProgramGenerator
from modernize.parser import SemanticIRNode

def test_evaluate_string_subject_uses_cobol_equals():
    var_types = {"WS-STATUS": "String"}
    trans = NativeStatementTranslator(var_types)
    
    node_eval = {
        "properties": {
            "statement_type": "EVALUATE",
            "subject": "WS-STATUS"
        }
    }
    node_when_active = {
        "properties": {
            "statement_type": "WHEN",
            "condition": '"ACTIVE"'
        }
    }
    node_when_other = {
        "properties": {
            "statement_type": "WHEN",
            "condition": "OTHER"
        }
    }
    
    assert trans.translate_statement(node_eval) is None
    res = trans.translate_statement(node_when_active)
    assert 'com.systema.modernized.CobolFormatHelper.cobolEquals(ws_status, "ACTIVE")' in res
    assert trans.translate_statement(node_when_other) == '} else {'

def test_if_condition_string_uses_cobol_equals():
    var_types = {"ITEM-STATUS": "String"}
    trans = NativeStatementTranslator(var_types)
    
    cond_eq = trans._translate_condition("ITEM-STATUS = 'ACTIVE'")
    cond_neq = trans._translate_condition("ITEM-STATUS NOT EQUAL 'ACTIVE'")
    
    assert cond_eq == 'com.systema.modernized.CobolFormatHelper.cobolEquals(item_status, "ACTIVE")'
    assert cond_neq == '!com.systema.modernized.CobolFormatHelper.cobolEquals(item_status, "ACTIVE")'

def test_level88_string_generation_uses_cobol_equals():
    ir_nodes = [
        SemanticIRNode(
            node_id=1, kind="VARIABLE",
            properties={"name": "WS-STATUS", "picture": "X(10)", "level": 1},
            source_file="test.cbl", source_line=1, source_column=1, start_offset=0, end_offset=0, status="PARSED"
        ),
        SemanticIRNode(
            node_id=2, kind="VARIABLE",
            properties={"name": "STATUS-OPEN", "level": 88, "condition_values": ["ACTIVE", "PENDING"]},
            source_file="test.cbl", source_line=2, source_column=1, start_offset=0, end_offset=0, status="PARSED"
        )
    ]
    gen = NativeProgramGenerator(program_name="TESTSTR", ir_nodes=ir_nodes)
    class_src = gen.generate_class_source()
    assert 'com.systema.modernized.CobolFormatHelper.cobolEquals(ws_status, "ACTIVE")' in class_src
    assert 'com.systema.modernized.CobolFormatHelper.cobolEquals(ws_status, "PENDING")' in class_src
