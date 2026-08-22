import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modernize.native_generator import NativeStatementTranslator

def test_move_multiple_targets():
    var_types = {"VAR-A": "String", "VAR-B": "BigDecimal", "VAR-C": "Integer"}
    trans = NativeStatementTranslator(var_types)
    
    node_move = {
        "properties": {
            "statement_type": "MOVE",
            "source": "100",
            "targets": ["VAR-B", "VAR-C"]
        }
    }
    
    java_stmt = trans.translate_statement(node_move)
    expected = 'var_b = new BigDecimal("100");\n        var_c = 100;'
    assert java_stmt == expected
