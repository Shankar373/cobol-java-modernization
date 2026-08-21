import re
from .lexer import CobolToken
from .semantic_ir import SemanticIR, SemanticIRNode

class ParserDiagnostic(Exception):
    def __init__(self, message: str, file: str, line: int, column: int, token_value: str, context: str):
        super().__init__(f"{message} at line {line}, col {column} (token: {token_value})")
        self.message = message
        self.file = file
        self.line = line
        self.column = column
        self.token_value = token_value
        self.context = context

    def to_dict(self) -> dict:
        return {
            "type": "PARSER_SYNTAX_ERROR",
            "message": self.message,
            "source_location": {
                "file": self.file,
                "line": self.line,
                "column": self.column
            },
            "offending_token": self.token_value,
            "context": self.context
        }


def parse_picture_clause(pic_str: str):
    pic = pic_str.upper()
    signed = pic.startswith("S")
    if signed:
        pic = pic[1:]
    
    expanded = []
    i = 0
    while i < len(pic):
        char = pic[i]
        if i + 1 < len(pic) and pic[i+1] == "(":
            end = pic.find(")", i + 1)
            if end != -1:
                try:
                    count = int(pic[i+2:end])
                    expanded.append(char * count)
                except ValueError:
                    expanded.append(char)
                i = end + 1
                continue
        expanded.append(char)
        i += 1
    
    expanded_str = "".join(expanded)
    if "V" in expanded_str:
        parts = expanded_str.split("V")
        digits = parts[0].count("9") + parts[1].count("9")
        scale = parts[1].count("9")
    else:
        digits = expanded_str.count("9")
        scale = 0
    
    return signed, digits, scale


COBOL_KEYWORDS = {
    "IDENTIFICATION", "PROGRAM-ID", "ENVIRONMENT", "CONFIGURATION", "INPUT-OUTPUT", "FILE-CONTROL",
    "SELECT", "ASSIGN", "ORGANIZATION", "INDEXED", "ACCESS", "DYNAMIC", "RECORD", "KEY", "STATUS",
    "DATA", "FILE", "FD", "WORKING-STORAGE", "LINKAGE", "PROCEDURE", "DIVISION", "SECTION",
    "MOVE", "TO", "ADD", "SUBTRACT", "MULTIPLY", "DIVIDE", "COMPUTE", "IF", "ELSE", "PERFORM", "THRU", "UNTIL",
    "DISPLAY", "GOBACK", "EXIT", "INITIALIZE", "READ", "WRITE", "REWRITE", "OPEN", "CLOSE",
    "STOP", "RUN", "COPY", "PIC", "PICTURE", "USAGE", "COMP", "COMP-3", "DISPLAY", "BINARY", "PACKED-DECIMAL",
    "REDEFINES", "OCCURS", "JUSTIFIED", "JUST", "VALUE", "VALUES", "WHEN", "TRUE", "FALSE", "EVALUATE",
    "END-IF", "END-PERFORM", "END-READ", "END-WRITE", "END-EVALUATE", "NOT", "EQUAL", "GREATER", "THAN", "LESS",
    "AND", "OR", "ON", "SIZE", "ERROR", "DECLARATIVES", "END-DECLARATIVES", "RETURN", "VARYING", "CALL", "USING"
}


STATEMENT_START_VERBS = {
    "MOVE", "COMPUTE", "ADD", "SUBTRACT", "MULTIPLY", "DIVIDE", "PERFORM", "CALL", "READ", "WRITE", 
    "REWRITE", "OPEN", "CLOSE", "STOP", "GOBACK", "IF", "ELSE", "END-IF", "THEN"
}


class CobolParser:
    def __init__(self, tokens: list, file_path: str):
        self.tokens = tokens
        self.file_path = file_path
        self.current = 0
        self.diagnostics = []
        self.ir = SemanticIR()
        self.node_counter = 0

    def next_node_id(self) -> str:
        self.node_counter += 1
        return f"node_{self.node_counter:05d}"

    def peek(self, offset: int = 0) -> CobolToken:
        if self.current + offset >= len(self.tokens):
            return CobolToken("EOF", "", self.file_path, 0, 0, 0, 0)
        return self.tokens[self.current + offset]

    def is_at_end(self) -> bool:
        return self.current >= len(self.tokens) or self.peek().type == "EOF"

    def check(self, type_: str, value: str = None) -> bool:
        if self.is_at_end():
            return False
        tok = self.peek()
        if tok.type != type_:
            return False
        if value is not None and tok.value.upper() != value.upper():
            return False
        return True

    def match(self, type_: str, value: str = None) -> bool:
        if self.check(type_, value):
            self.current += 1
            return True
        return False

    def consume(self, type_: str, value: str = None, message: str = "Expected token") -> CobolToken:
        if self.check(type_, value):
            tok = self.peek()
            self.current += 1
            return tok
        
        offending = self.peek()
        diag = ParserDiagnostic(
            message=message,
            file=self.file_path,
            line=offending.line,
            column=offending.column,
            token_value=offending.value,
            context=f"Parsing around token {offending.value}"
        )
        self.diagnostics.append(diag)
        raise diag

    def consume_val(self, message: str = "Expected identifier or literal") -> CobolToken:
        tok = self.peek()
        if tok.type in ("IDENTIFIER", "LITERAL_STRING", "LITERAL_NUMBER", "KEYWORD"):
            self.current += 1
            return tok
        
        diag = ParserDiagnostic(
            message=message,
            file=self.file_path,
            line=tok.line,
            column=tok.column,
            token_value=tok.value,
            context=f"Parsing value around {tok.value}"
        )
        self.diagnostics.append(diag)
        raise diag

    def parse(self) -> SemanticIR:
        while not self.is_at_end():
            try:
                if self.check("KEYWORD", "IDENTIFICATION") or self.check("KEYWORD", "ID"):
                    self.parse_identification_division()
                elif self.check("KEYWORD", "ENVIRONMENT"):
                    self.parse_environment_division()
                elif self.check("KEYWORD", "DATA"):
                    self.parse_data_division()
                elif self.check("KEYWORD", "PROCEDURE"):
                    self.parse_procedure_division()
                else:
                    self.current += 1
            except ParserDiagnostic:
                # Recover to next division
                while not self.is_at_end() and not self.check("KEYWORD", "ENVIRONMENT") and not self.check("KEYWORD", "DATA") and not self.check("KEYWORD", "PROCEDURE"):
                    self.current += 1
        return self.ir

    def parse_identification_division(self):
        start_tok = self.peek()
        if self.match("KEYWORD", "IDENTIFICATION") or self.match("KEYWORD", "ID"):
            self.consume("KEYWORD", "DIVISION", "Expected DIVISION keyword")
            self.consume("PUNCTUATION", ".", "Expected period after DIVISION")
        
        node = SemanticIRNode(
            node_id=self.next_node_id(),
            kind="DIVISION",
            properties={"name": "IDENTIFICATION"},
            source_file=self.file_path,
            source_line=start_tok.line,
            source_column=start_tok.column,
            start_offset=start_tok.start_offset,
            end_offset=self.peek().start_offset,
            status="PARSED"
        )
        self.ir.add_node(node)

        # Parse PROGRAM-ID
        if self.match("KEYWORD", "PROGRAM-ID"):
            self.consume("PUNCTUATION", ".", "Expected period after PROGRAM-ID")
            prog_name_tok = self.consume("IDENTIFIER", None, "Expected program name identifier")
            self.consume("PUNCTUATION", ".", "Expected period after program name")
            
            p_node = SemanticIRNode(
                node_id=self.next_node_id(),
                kind="PROGRAM",
                properties={"name": prog_name_tok.value},
                source_file=self.file_path,
                source_line=prog_name_tok.line,
                source_column=prog_name_tok.column,
                start_offset=prog_name_tok.start_offset,
                end_offset=self.peek().start_offset,
                status="PARSED"
            )
            self.ir.add_node(p_node)

    def parse_environment_division(self):
        start_tok = self.peek()
        self.consume("KEYWORD", "ENVIRONMENT", "Expected ENVIRONMENT")
        self.consume("KEYWORD", "DIVISION", "Expected DIVISION")
        self.consume("PUNCTUATION", ".", "Expected period")

        node = SemanticIRNode(
            node_id=self.next_node_id(),
            kind="DIVISION",
            properties={"name": "ENVIRONMENT"},
            source_file=self.file_path,
            source_line=start_tok.line,
            source_column=start_tok.column,
            start_offset=start_tok.start_offset,
            end_offset=self.peek().start_offset,
            status="PARSED"
        )
        self.ir.add_node(node)

        while not self.is_at_end() and not self.check("KEYWORD", "DATA") and not self.check("KEYWORD", "PROCEDURE"):
            if self.match("KEYWORD", "CONFIGURATION") or self.match("KEYWORD", "INPUT-OUTPUT"):
                name = self.peek(-1).value
                self.consume("KEYWORD", "SECTION", "Expected SECTION")
                self.consume("PUNCTUATION", ".", "Expected period")
                
                sec_node = SemanticIRNode(
                    node_id=self.next_node_id(),
                    kind="SECTION",
                    properties={"name": name},
                    source_file=self.file_path,
                    source_line=start_tok.line,
                    source_column=start_tok.column,
                    start_offset=start_tok.start_offset,
                    end_offset=self.peek().start_offset,
                    status="PARSED"
                )
                self.ir.add_node(sec_node)
            else:
                self.current += 1

    def parse_data_division(self):
        start_tok = self.peek()
        self.consume("KEYWORD", "DATA", "Expected DATA")
        self.consume("KEYWORD", "DIVISION", "Expected DIVISION")
        self.consume("PUNCTUATION", ".", "Expected period")

        node = SemanticIRNode(
            node_id=self.next_node_id(),
            kind="DIVISION",
            properties={"name": "DATA"},
            source_file=self.file_path,
            source_line=start_tok.line,
            source_column=start_tok.column,
            start_offset=start_tok.start_offset,
            end_offset=self.peek().start_offset,
            status="PARSED"
        )
        self.ir.add_node(node)

        while not self.is_at_end() and not self.check("KEYWORD", "PROCEDURE"):
            if self.match("KEYWORD", "FILE") or self.match("KEYWORD", "WORKING-STORAGE") or self.match("KEYWORD", "LINKAGE"):
                sec_name = self.peek(-1).value
                self.consume("KEYWORD", "SECTION", "Expected SECTION")
                self.consume("PUNCTUATION", ".", "Expected period")
                
                sec_node = SemanticIRNode(
                    node_id=self.next_node_id(),
                    kind="SECTION",
                    properties={"name": sec_name},
                    source_file=self.file_path,
                    source_line=start_tok.line,
                    source_column=start_tok.column,
                    start_offset=start_tok.start_offset,
                    end_offset=self.peek().start_offset,
                    status="PARSED"
                )
                self.ir.add_node(sec_node)
                self.parse_data_items()
            else:
                self.current += 1

    def parse_data_items(self):
        while not self.is_at_end() and not self.check("KEYWORD", "PROCEDURE") and not self.check("KEYWORD", "FILE") and not self.check("KEYWORD", "WORKING-STORAGE") and not self.check("KEYWORD", "LINKAGE"):
            if self.check("LITERAL_NUMBER"):
                lvl_tok = self.peek()
                lvl = int(lvl_tok.value)
                
                if lvl not in (1, 5, 10, 77, 88):
                    self.current += 1
                    continue
                
                self.current += 1
                
                name_tok = self.peek()
                if self.check("IDENTIFIER") or self.check("KEYWORD"):
                    self.current += 1
                    name = name_tok.value
                else:
                    name = "FILLER"
                
                props = {
                    "name": name,
                    "level": lvl,
                    "picture": None,
                    "usage": None,
                    "value": None,
                    "redefines": None,
                    "occurs": None,
                    "signed": False,
                    "digits": 0,
                    "scale": 0,
                    "is_group": True,
                    "condition_values": []
                }
                
                while not self.is_at_end() and not self.check("PUNCTUATION", "."):
                    if self.match("KEYWORD", "REDEFINES"):
                        ref_tok = self.consume("IDENTIFIER", None, "Expected identifier after REDEFINES")
                        props["redefines"] = ref_tok.value
                    
                    elif self.match("KEYWORD", "PIC") or self.match("KEYWORD", "PICTURE"):
                        self.match("KEYWORD", "IS")
                        
                        pic_parts = []
                        while not self.is_at_end() and not self.check("KEYWORD") and not self.check("PUNCTUATION", "."):
                            pic_parts.append(self.peek().value)
                            self.current += 1
                        
                        pic_str = "".join(pic_parts)
                        props["picture"] = pic_str
                        props["is_group"] = False
                        
                        signed, digits, scale = parse_picture_clause(pic_str)
                        props["signed"] = signed
                        props["digits"] = digits
                        props["scale"] = scale
                        
                    elif self.match("KEYWORD", "USAGE"):
                        self.match("KEYWORD", "IS")
                        usage_tok = self.peek()
                        self.current += 1
                        props["usage"] = usage_tok.value.upper()
                        
                    elif self.match("KEYWORD", "COMP") or self.match("KEYWORD", "COMP-3") or self.match("KEYWORD", "BINARY") or self.match("KEYWORD", "DISPLAY"):
                        props["usage"] = self.peek(-1).value.upper()
                        
                    elif self.match("KEYWORD", "VALUE") or self.match("KEYWORD", "VALUES"):
                        self.match("KEYWORD", "IS")
                        val_tok = self.peek()
                        self.current += 1
                        props["value"] = val_tok.value
                        
                        if lvl == 88:
                            props["condition_values"].append(val_tok.value)
                            
                    elif self.match("KEYWORD", "OCCURS"):
                        times_tok = self.consume("LITERAL_NUMBER", None, "Expected count after OCCURS")
                        props["occurs"] = int(times_tok.value)
                        self.match("KEYWORD", "TIMES")
                    else:
                        self.current += 1
                
                self.consume("PUNCTUATION", ".", "Expected period after data item definition")
                
                node = SemanticIRNode(
                    node_id=self.next_node_id(),
                    kind="DATA_ITEM",
                    properties=props,
                    source_file=self.file_path,
                    source_line=lvl_tok.line,
                    source_column=lvl_tok.column,
                    start_offset=lvl_tok.start_offset,
                    end_offset=self.peek().start_offset,
                    status="PARSED"
                )
                self.ir.add_node(node)
            else:
                self.current += 1

    def parse_procedure_division(self):
        start_tok = self.peek()
        self.consume("KEYWORD", "PROCEDURE", "Expected PROCEDURE")
        self.consume("KEYWORD", "DIVISION", "Expected DIVISION")
        if self.match("KEYWORD", "USING"):
            while not self.is_at_end() and not self.check("PUNCTUATION", "."):
                self.current += 1
        
        self.consume("PUNCTUATION", ".", "Expected period")

        node = SemanticIRNode(
            node_id=self.next_node_id(),
            kind="DIVISION",
            properties={"name": "PROCEDURE"},
            source_file=self.file_path,
            source_line=start_tok.line,
            source_column=start_tok.column,
            start_offset=start_tok.start_offset,
            end_offset=self.peek().start_offset,
            status="PARSED"
        )
        self.ir.add_node(node)

        while not self.is_at_end():
            if self.check("IDENTIFIER") and self.peek(1).type == "PUNCTUATION" and self.peek(1).value == ".":
                name_tok = self.peek()
                self.current += 2
                
                kind = "PARAGRAPH"
                if self.match("KEYWORD", "SECTION"):
                    kind = "SECTION"
                    self.consume("PUNCTUATION", ".", "Expected period after SECTION")
                
                p_node = SemanticIRNode(
                    node_id=self.next_node_id(),
                    kind=kind,
                    properties={"name": name_tok.value},
                    source_file=self.file_path,
                    source_line=name_tok.line,
                    source_column=name_tok.column,
                    start_offset=name_tok.start_offset,
                    end_offset=self.peek().start_offset,
                    status="PARSED"
                )
                self.ir.add_node(p_node)
            else:
                self.parse_statement()

    def parse_statement(self):
        try:
            self._parse_statement_internal()
        except ParserDiagnostic:
            while not self.is_at_end() and not self.check("PUNCTUATION", ".") and not self.check("KEYWORD", "MOVE") and not self.check("KEYWORD", "IF") and not self.check("KEYWORD", "PERFORM"):
                self.current += 1
            self.match("PUNCTUATION", ".")

    def _parse_statement_internal(self):
        start_tok = self.peek()
        
        if self.match("KEYWORD", "MOVE"):
            src_tok = self.consume_val("Expected source identifier or literal in MOVE")
            self.consume("KEYWORD", "TO", "Expected TO keyword")
            tgt_tok = self.consume("IDENTIFIER", None, "Expected target identifier")
            self.match("PUNCTUATION", ".")
            
            node = SemanticIRNode(
                node_id=self.next_node_id(),
                kind="STATEMENT",
                properties={
                    "statement_type": "MOVE",
                    "source": src_tok.value,
                    "target": tgt_tok.value
                },
                source_file=self.file_path,
                source_line=start_tok.line,
                source_column=start_tok.column,
                start_offset=start_tok.start_offset,
                end_offset=self.peek().start_offset,
                status="PARSED"
            )
            self.ir.add_node(node)
            
        elif self.match("KEYWORD", "COMPUTE"):
            tgt_tok = self.consume("IDENTIFIER", None, "Expected target identifier")
            self.consume("PUNCTUATION", "=", "Expected '=' in COMPUTE")
            
            expr_parts = []
            while not self.is_at_end() and not self.check("PUNCTUATION", ".") and not self.check("KEYWORD"):
                tok = self.peek()
                if tok.type in ("IDENTIFIER", "LITERAL_NUMBER", "PUNCTUATION"):
                    expr_parts.append(tok.value)
                    self.current += 1
                else:
                    break
            
            self.match("PUNCTUATION", ".")
            
            node = SemanticIRNode(
                node_id=self.next_node_id(),
                kind="STATEMENT",
                properties={
                    "statement_type": "COMPUTE",
                    "target": tgt_tok.value,
                    "expression": " ".join(expr_parts)
                },
                source_file=self.file_path,
                source_line=start_tok.line,
                source_column=start_tok.column,
                start_offset=start_tok.start_offset,
                end_offset=self.peek().start_offset,
                status="PARSED"
            )
            self.ir.add_node(node)

        elif self.match("KEYWORD", "ADD") or self.match("KEYWORD", "SUBTRACT") or self.match("KEYWORD", "MULTIPLY") or self.match("KEYWORD", "DIVIDE"):
            op = self.peek(-1).value.upper()
            val_tok = self.consume_val("Expected value to perform calculation")
            self.consume("KEYWORD", "TO", "Expected TO keyword")
            tgt_tok = self.consume("IDENTIFIER", None, "Expected target identifier")
            self.match("PUNCTUATION", ".")
            
            node = SemanticIRNode(
                node_id=self.next_node_id(),
                kind="STATEMENT",
                properties={
                    "statement_type": op,
                    "value": val_tok.value,
                    "target": tgt_tok.value
                },
                source_file=self.file_path,
                source_line=start_tok.line,
                source_column=start_tok.column,
                start_offset=start_tok.start_offset,
                end_offset=self.peek().start_offset,
                status="PARSED"
            )
            self.ir.add_node(node)

        elif self.match("KEYWORD", "IF"):
            cond_parts = []
            while not self.is_at_end() and not self.check("PUNCTUATION", "."):
                tok = self.peek()
                if tok.type == "KEYWORD" and tok.value.upper() in STATEMENT_START_VERBS:
                    break
                self.current += 1
                cond_parts.append(tok.value)
            
            self.match("KEYWORD", "THEN")
            
            node = SemanticIRNode(
                node_id=self.next_node_id(),
                kind="STATEMENT",
                properties={
                    "statement_type": "IF",
                    "condition": " ".join(cond_parts)
                },
                source_file=self.file_path,
                source_line=start_tok.line,
                source_column=start_tok.column,
                start_offset=start_tok.start_offset,
                end_offset=self.peek().start_offset,
                status="PARSED"
            )
            self.ir.add_node(node)

        elif self.match("KEYWORD", "ELSE"):
            node = SemanticIRNode(
                node_id=self.next_node_id(),
                kind="STATEMENT",
                properties={"statement_type": "ELSE"},
                source_file=self.file_path,
                source_line=start_tok.line,
                source_column=start_tok.column,
                start_offset=start_tok.start_offset,
                end_offset=self.peek().start_offset,
                status="PARSED"
            )
            self.ir.add_node(node)

        elif self.match("KEYWORD", "PERFORM"):
            tgt_tok = self.consume("IDENTIFIER", None, "Expected paragraph name after PERFORM")
            
            props = {"statement_type": "PERFORM", "target": tgt_tok.value}
            if self.match("KEYWORD", "THRU"):
                thru_tok = self.consume("IDENTIFIER", None, "Expected THRU paragraph name")
                props["thru"] = thru_tok.value
            
            self.match("PUNCTUATION", ".")
            
            node = SemanticIRNode(
                node_id=self.next_node_id(),
                kind="STATEMENT",
                properties=props,
                source_file=self.file_path,
                source_line=start_tok.line,
                source_column=start_tok.column,
                start_offset=start_tok.start_offset,
                end_offset=self.peek().start_offset,
                status="PARSED"
            )
            self.ir.add_node(node)

        elif self.match("KEYWORD", "CALL"):
            tgt_tok = self.consume_val("Expected subprogram target name")
            
            args = []
            if self.match("KEYWORD", "USING"):
                while not self.is_at_end() and not self.check("PUNCTUATION", ".") and not self.check("KEYWORD"):
                    tok = self.consume_val("Expected USING argument name")
                    args.append(tok.value)
            
            self.match("PUNCTUATION", ".")
            
            node = SemanticIRNode(
                node_id=self.next_node_id(),
                kind="STATEMENT",
                properties={
                    "statement_type": "CALL",
                    "target": tgt_tok.value,
                    "arguments": args
                },
                source_file=self.file_path,
                source_line=start_tok.line,
                source_column=start_tok.column,
                start_offset=start_tok.start_offset,
                end_offset=self.peek().start_offset,
                status="PARSED"
            )
            self.ir.add_node(node)

        elif self.match("KEYWORD", "READ") or self.match("KEYWORD", "WRITE") or self.match("KEYWORD", "REWRITE"):
            op = self.peek(-1).value.upper()
            file_tok = self.consume("IDENTIFIER", None, f"Expected file identifier after {op}")
            self.match("PUNCTUATION", ".")
            
            node = SemanticIRNode(
                node_id=self.next_node_id(),
                kind="STATEMENT",
                properties={
                    "statement_type": op,
                    "target": file_tok.value
                },
                source_file=self.file_path,
                source_line=start_tok.line,
                source_column=start_tok.column,
                start_offset=start_tok.start_offset,
                end_offset=self.peek().start_offset,
                status="PARSED"
            )
            self.ir.add_node(node)

        elif self.match("KEYWORD", "OPEN") or self.match("KEYWORD", "CLOSE"):
            op = self.peek(-1).value.upper()
            file_tok = self.consume_val(f"Expected file identifier/mode after {op}")
            self.match("PUNCTUATION", ".")
            
            node = SemanticIRNode(
                node_id=self.next_node_id(),
                kind="STATEMENT",
                properties={
                    "statement_type": op,
                    "target": file_tok.value
                },
                source_file=self.file_path,
                source_line=start_tok.line,
                source_column=start_tok.column,
                start_offset=start_tok.start_offset,
                end_offset=self.peek().start_offset,
                status="PARSED"
            )
            self.ir.add_node(node)

        elif self.match("KEYWORD", "STOP") or self.match("KEYWORD", "GOBACK"):
            val = self.peek(-1).value.upper()
            if val == "STOP":
                self.consume("KEYWORD", "RUN", "Expected RUN after STOP")
                val = "STOP RUN"
            self.match("PUNCTUATION", ".")
            
            node = SemanticIRNode(
                node_id=self.next_node_id(),
                kind="STATEMENT",
                properties={
                    "statement_type": val
                },
                source_file=self.file_path,
                source_line=start_tok.line,
                source_column=start_tok.column,
                start_offset=start_tok.start_offset,
                end_offset=self.peek().start_offset,
                status="PARSED"
            )
            self.ir.add_node(node)

        elif self.match("KEYWORD", "END-IF") or self.match("KEYWORD", "END-PERFORM") or self.match("KEYWORD", "END-READ") or self.match("KEYWORD", "END-WRITE") or self.match("KEYWORD", "END-EVALUATE"):
            val = self.peek(-1).value.upper()
            self.match("PUNCTUATION", ".")
            
            node = SemanticIRNode(
                node_id=self.next_node_id(),
                kind="STATEMENT",
                properties={
                    "statement_type": val
                },
                source_file=self.file_path,
                source_line=start_tok.line,
                source_column=start_tok.column,
                start_offset=start_tok.start_offset,
                end_offset=self.peek().start_offset,
                status="PARSED"
            )
            self.ir.add_node(node)

        else:
            tok = self.peek()
            self.current += 1
            
            node = SemanticIRNode(
                node_id=self.next_node_id(),
                kind="STATEMENT",
                properties={
                    "statement_type": "UNKNOWN",
                    "offending_token": tok.value
                },
                source_file=self.file_path,
                source_line=start_tok.line,
                source_column=start_tok.column,
                start_offset=start_tok.start_offset,
                end_offset=self.peek().start_offset,
                status="UNSUPPORTED"
            )
            self.ir.add_node(node)
