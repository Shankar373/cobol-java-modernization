import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modernize.lexer import CobolLexer
from modernize.parser import CobolParser
from modernize.native_generator import NativeProgramGenerator

def test_adversarial_validation_complete():
    # Read the synthetic adversarial COBOL code
    cob_path = "tests/repos/ADVERSARIAL01/ADVERSARIAL01.cob"
    assert os.path.exists(cob_path)
    
    with open(cob_path, "r", encoding="utf-8") as fh:
        content = fh.read()
        
    lexer = CobolLexer(cob_path)
    tokens = lexer.tokenize(content)
    parser = CobolParser(tokens, cob_path)
    ir = parser.parse()
    
    gen = NativeProgramGenerator("ADVERSARIAL01", list(ir.nodes.values()))
    
    # Verify mapping discovery
    assert "WS-STATUS" in gen.var_types
    assert "STATUS-OPEN" in gen.level88_map
    assert "ITEM-AMOUNT" not in gen.var_types  # group item
    assert "ITEM-VAL" in gen.var_types  # array item
    assert "ITEM-VAL" in gen.occurs_map
    
    print("\nDEBUG gen.var_types:", gen.var_types)
    java_src = gen.generate_class_source()
    print("\nDEBUG java_src:\n", java_src)
    
    # 1. Verify java.util.Objects is imported
    assert "import java.util.Objects;" in java_src
    
    # 2. Verify OCCURS array declaration
    assert "public BigDecimal[] item_val = new BigDecimal[5];" in java_src
    assert "java.util.Arrays.fill(item_val, BigDecimal.ZERO);" in java_src
    
    # 3. Verify Level-88 helper method
    assert "public boolean isStatusOpen() { return Objects.equals(ws_status, \"O\"); }" in java_src
    
    # 4. Verify EVALUATE translation
    assert "if (Objects.equals(ws_status, \"O\")) {" in java_src
    
    # 5. Verify IF Level-88 translation
    assert "if (isStatusOpen()) {" in java_src
    
    # 6. Verify MULTI-MOVE translation
    assert "ws_target_1 = 10;" in java_src
    assert "ws_target_2 = 10;" in java_src
    
    # 7. Verify PERFORM VARYING translation
    assert "for (ws_i = 1; !(ws_i > ws_limit); ws_i += 1) {" in java_src
    
    # 8. Verify subscripted element assignment
    assert "item_val[ws_i - 1] = new BigDecimal(\"2.50\");" in java_src
    
    assert 'System.out.println("ARRAY_ITEM(" + " " + String.format("%01d", ws_i) + " " + ")=" + " " + String.format("%05d", item_val[ws_i - 1].movePointRight(2).longValue()));' in java_src
