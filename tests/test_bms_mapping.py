import pytest
from modernize.bms_parser import BmsParser

def test_bms_parser_simple():
    bms_src = """
MSET1    DFHMSD TYPE=&SYSPARM,MODE=INOUT,LANG=COBOL,STORAGE=AUTO,      *
               CTRL=FREEKB,TERM=3270
MAP1     DFHMDI SIZE=(24,80)
FIELD1   DFHMDF POS=(05,10),LENGTH=15,INITIAL='CUSTOMER NAME',         *
               ATTRB=(ASKIP,BRT)
         DFHMDF POS=(05,26),LENGTH=1,ATTRB=ASKIP
NAME     DFHMDF POS=(06,10),LENGTH=30,ATTRB=(UNPROT,IC)
    """
    parser = BmsParser(bms_src)
    mapset = parser.parse()
    
    assert mapset.name == "MSET1"
    assert len(mapset.maps) == 1
    
    map1 = mapset.maps[0]
    assert map1.name == "MAP1"
    assert map1.size == (24, 80)
    assert len(map1.fields) == 3
    
    f1 = map1.fields[0]
    assert f1.name == "FIELD1"
    assert f1.pos == (5, 10)
    assert f1.length == 15
    assert f1.initial == "CUSTOMER NAME"
    assert "ASKIP" in f1.attrb
    assert "BRT" in f1.attrb

    f2 = map1.fields[1]
    assert f2.name == "" # Unnamed
    assert f2.pos == (5, 26)
    assert f2.length == 1
    assert f2.attrb == ["ASKIP"]

    f3 = map1.fields[2]
    assert f3.name == "NAME"
    assert f3.pos == (6, 10)
    assert f3.length == 30
    assert "UNPROT" in f3.attrb
    assert "IC" in f3.attrb
