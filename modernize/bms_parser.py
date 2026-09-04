import re

class BmsField:
    def __init__(self, name, pos, length, initial=None, attrb=None):
        self.name = name
        self.pos = pos # (row, col)
        self.length = length
        self.initial = initial
        self.attrb = attrb or []

    def to_dict(self):
        return {
            "name": self.name,
            "pos": self.pos,
            "length": self.length,
            "initial": self.initial,
            "attrb": self.attrb
        }

class BmsMap:
    def __init__(self, name, size=None):
        self.name = name
        self.size = size # (rows, cols)
        self.fields = []

    def to_dict(self):
        return {
            "name": self.name,
            "size": self.size,
            "fields": [f.to_dict() for f in self.fields]
        }

class BmsMapset:
    def __init__(self, name):
        self.name = name
        self.maps = []

    def to_dict(self):
        return {
            "name": self.name,
            "maps": [m.to_dict() for m in self.maps]
        }

class BmsParser:
    def __init__(self, content):
        self.content = content

    def parse(self) -> BmsMapset:
        # Pre-process lines to join continuation lines
        raw_lines = self.content.splitlines()
        joined_lines = []
        i = 0
        n = len(raw_lines)
        
        while i < n:
            line = raw_lines[i]
            # Strip trailing comments if they are separated by spaces or * in column 72
            # Mainframe JCL/BMS rules: if column 72 (1-indexed, i.e., index 71) has a non-blank character,
            # it indicates continuation.
            is_continued = False
            if len(line) >= 72:
                col72 = line[71]
                if col72 != ' ' and col72 != '\n':
                    is_continued = True
                    line = line[:71]
            
            stripped = line.rstrip()
            if is_continued or stripped.endswith(','):
                # Consume next line and join
                while i + 1 < n:
                    next_line = raw_lines[i+1]
                    next_continued = False
                    if len(next_line) >= 72:
                        next_col72 = next_line[71]
                        if next_col72 != ' ' and next_col72 != '\n':
                            next_continued = True
                            next_line = next_line[:71]
                    
                    line += " " + next_line.strip()
                    i += 1
                    if not next_continued and not next_line.rstrip().endswith(','):
                        break
            joined_lines.append(line)
            i += 1

        mapset = BmsMapset("UNNAMED")
        current_map = None

        for line in joined_lines:
            if not line or line.startswith('*'):
                continue
                
            stripped = line.strip()
            if not stripped:
                continue

            # Standard pattern: LABEL TYPE PARAMETERS
            # If line starts with whitespace, label is empty ""
            if line[0].isspace():
                parts = stripped.split(None, 1)
                label = ""
                macro_type = parts[0].upper() if len(parts) > 0 else ""
                params_str = parts[1] if len(parts) > 1 else ""
            else:
                parts = stripped.split(None, 2)
                label = parts[0]
                macro_type = parts[1].upper() if len(parts) > 1 else ""
                params_str = parts[2] if len(parts) > 2 else ""

            if macro_type == "DFHMSD":
                if label:
                    mapset.name = label
            elif macro_type == "DFHMDI":
                size = self._parse_size(params_str)
                current_map = BmsMap(label, size)
                mapset.maps.append(current_map)
            elif macro_type == "DFHMDF":
                if current_map is not None:
                    field = self._parse_field(label, params_str)
                    if field:
                        current_map.fields.append(field)

        return mapset

    def _parse_size(self, params_str):
        # SIZE=(rows, cols)
        m = re.search(r'SIZE\s*=\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)', params_str, re.IGNORECASE)
        if m:
            return (int(m.group(1)), int(m.group(2)))
        return (24, 80)

    def _parse_field(self, label, params_str) -> BmsField:
        # DFHMDF options: POS=(row,col), LENGTH=len, INITIAL='...', ATTRB=(...)
        # Find POS
        pos = (1, 1)
        m_pos = re.search(r'POS\s*=\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)', params_str, re.IGNORECASE)
        if m_pos:
            pos = (int(m_pos.group(1)), int(m_pos.group(2)))
            
        # Find LENGTH
        length = 1
        m_len = re.search(r'LENGTH\s*=\s*(\d+)', params_str, re.IGNORECASE)
        if m_len:
            length = int(m_len.group(1))
            
        # Find INITIAL
        initial = None
        m_init = re.search(r'INITIAL\s*=\s*[\'"]([^\'"]*)[\'"]', params_str, re.IGNORECASE)
        if m_init:
            initial = m_init.group(1)
            
        # Find ATTRB
        attrb = []
        m_attr = re.search(r'ATTRB\s*=\s*\(\s*([^\)]+)\s*\)', params_str, re.IGNORECASE)
        if m_attr:
            attrb = [x.strip().upper() for x in m_attr.group(1).split(',')]
        else:
            # Single value without parenthesis
            m_attr_single = re.search(r'ATTRB\s*=\s*([A-Z0-9]+)', params_str, re.IGNORECASE)
            if m_attr_single:
                attrb = [m_attr_single.group(1).upper()]

        # If label is DFHMDF or empty, field is unnamed
        name = label if label.upper() != "DFHMDF" else ""
        return BmsField(name, pos, length, initial, attrb)
