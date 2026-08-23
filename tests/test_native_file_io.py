import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modernize.native_generator import NativeFileIOGenerator

def test_generate_io_methods_input():
    record_fields = [
        ("FIELD-A", "X(5)"),
        ("FIELD-B", "9(3)"),
        ("FIELD-C", "9(4)V99")
    ]
    res = NativeFileIOGenerator.generate_io_methods("FILE-A", "input.dat", True, record_fields)
    
    assert "private BufferedReader file_a_reader;" in res
    assert "file_a_reader = Files.newBufferedReader(Paths.get(resolve_path_file_a()));" in res
    assert "field_a = val;" in res
    assert "field_b = val.isEmpty() ? 0 : Integer.parseInt(val);" in res
    assert "field_c = val.isEmpty() ? BigDecimal.ZERO : new BigDecimal(val).movePointLeft(2);" in res

def test_generate_io_methods_output():
    record_fields = [
        ("OUT-FIELD-A", "X(10)"),
        ("OUT-FIELD-B", "9(5)")
    ]
    res = NativeFileIOGenerator.generate_io_methods("FILE-B", "output.dat", False, record_fields)
    
    assert "private BufferedWriter file_b_writer;" in res
    assert "file_b_writer = Files.newBufferedWriter(Paths.get(resolve_path_file_b()));" in res
    assert "write_file_b" in res
    assert "String.format(\"%-10s%05d\"" in res
