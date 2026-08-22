import re
import os
from decimal import Decimal

def to_java_var(name: str) -> str:
    # Check if name has subscript, e.g. ITEM-AMOUNT(3) or ITEM-AMOUNT ( WS-I )
    match = re.match(r'^([A-Za-z0-9_-]+)\s*\(\s*([^()]+)\s*\)$', name)
    if match:
        base = match.group(1).replace("-", "_").lower()
        idx = match.group(2).strip()
        idx_java = to_java_var(idx)
        if idx_java.isdigit():
            return f"{base}[{int(idx_java) - 1}]"
        return f"{base}[{idx_java} - 1]"

    name = name.replace("-", "_").lower()
    if name in ("class", "public", "private", "protected", "static", "final", "void", 
                "int", "double", "float", "long", "short", "char", "boolean", "byte", "new", "import", "package"):
        name = name + "_"
    return name

def to_java_method(name: str) -> str:
    parts = name.replace("-", "_").split("_")
    camel = "".join(p.capitalize() for p in parts if p)
    return "is" + camel


def is_input_file(logical: str, path: str) -> bool:
    logical_upper = logical.upper()
    path_lower = path.lower()
    if "IN-" in logical_upper or "SOURCE" in logical_upper or "SLS" in logical_upper or "INPUT" in logical_upper or "FILE-A" in logical_upper or "FILE-B" in logical_upper:
        return True
    if "OUT-" in logical_upper or "REPORT" in logical_upper or "RESULT" in logical_upper or "RPT" in logical_upper or "OUTPUT" in logical_upper:
        return False
    if "in" in path_lower or "source" in path_lower or "input" in path_lower:
        return True
    if "out" in path_lower or "report" in path_lower or "result" in path_lower:
        return False
    return True

def to_java_class(name: str) -> str:
    parts = name.replace("-", "_").split("_")
    return "".join(p.capitalize() for p in parts if p)

class NativeTypeMapper:
    @staticmethod
    def parse_pic(pic_str: str):
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
        if "X" in expanded_str or "Z" in expanded_str:
            return "String", len(expanded_str), 0, signed
        
        if "V" in expanded_str:
            parts = expanded_str.split("V")
            digits = parts[0].count("9") + parts[1].count("9")
            scale = parts[1].count("9")
            return "BigDecimal", digits, scale, signed
        else:
            digits = expanded_str.count("9")
            return "Integer" if digits <= 9 else "Long", digits, 0, signed

    @classmethod
    def get_java_type(cls, pic_str: str, usage: str = None) -> str:
        if usage and usage.upper() in ("COMP-3", "PACKED-DECIMAL"):
            return "BigDecimal"
        
        t_name, _, _, _ = cls.parse_pic(pic_str)
        return t_name

class NativeExpressionTranslator:
    def __init__(self, variables_types: dict):
        self.var_types = variables_types

    def _translate_subscripts(self, expr: str) -> str:
        pattern = r'(?<![A-Za-z0-9_-])([A-Za-z0-9_-]+)\s*\(\s*([^()]+)\s*\)'
        def repl(match):
            var_name = to_java_var(match.group(1))
            idx = match.group(2).strip()
            for v in self.var_types.keys():
                idx = re.sub(r'\b' + re.escape(v) + r'\b', to_java_var(v), idx)
            if idx.isdigit():
                return f"{var_name}[{int(idx) - 1}]"
            return f"{var_name}[{idx} - 1]"
        
        old = ""
        while old != expr:
            old = expr
            expr = re.sub(pattern, repl, expr)
        return expr

    def translate(self, expr_str: str) -> str:
        expr_str = self._translate_subscripts(expr_str)
        tokens = re.split(r'(\s+[\+\-\*\/]\s+|\(|\))', expr_str)
        
        translated_tokens = []
        for t in tokens:
            t_strip = t.strip()
            if not t_strip:
                continue
            if t_strip in ("+", "-", "*", "/", "(", ")"):
                translated_tokens.append(t_strip)
            elif re.match(r'^\d+(\.\d+)?$', t_strip):
                translated_tokens.append(f"new BigDecimal(\"{t_strip}\")")
            else:
                if "[" in t_strip:
                    base_java = re.split(r'\[', t_strip)[0].strip()
                    v_type = "BigDecimal"
                    for cobol_var, c_type in self.var_types.items():
                        if to_java_var(cobol_var) == base_java:
                            v_type = c_type
                            break
                    if v_type in ("Integer", "Long"):
                        translated_tokens.append(f"BigDecimal.valueOf({t_strip})")
                    else:
                        translated_tokens.append(t_strip)
                else:
                    java_var = to_java_var(t_strip)
                    v_type = self.var_types.get(t_strip, "BigDecimal")
                    if v_type in ("Integer", "Long"):
                        translated_tokens.append(f"BigDecimal.valueOf({java_var})")
                    else:
                        translated_tokens.append(java_var)

        return self._convert_to_bigdecimal_calls(translated_tokens)

    def _convert_to_bigdecimal_calls(self, tokens: list) -> str:
        if not tokens:
            return "BigDecimal.ZERO"
        if len(tokens) == 1:
            return tokens[0]

        try:
            return self._parse_infix(tokens)
        except Exception:
            return "BigDecimal.ZERO"

    def _parse_infix(self, tokens: list) -> str:
        idx = 0
        def peek():
            nonlocal idx
            return tokens[idx] if idx < len(tokens) else None
        
        def consume():
            nonlocal idx
            val = peek()
            idx += 1
            return val
        
        def parse_factor() -> str:
            t = peek()
            if t == "(":
                consume()
                expr = parse_expr()
                consume()
                return expr
            return consume()

        def parse_term() -> str:
            left = parse_factor()
            while peek() in ("*", "/"):
                op = consume()
                right = parse_factor()
                if op == "*":
                    left = f"{left}.multiply({right})"
                else:
                    left = f"{left}.divide({right}, 2, RoundingMode.DOWN)"
            return left

        def parse_expr() -> str:
            left = parse_term()
            while peek() in ("+", "-"):
                op = consume()
                right = parse_term()
                if op == "+":
                    left = f"{left}.add({right})"
                else:
                    left = f"{left}.subtract({right})"
            return left

        return parse_expr()

class NativeStatementTranslator:
    def __init__(self, var_types: dict, file_assigns: list = None, record_to_fd: dict = None, all_generators: dict = None, current_generator = None, level88_map: dict = None):
        self.var_types = var_types
        self.file_assigns = file_assigns or []
        self.record_to_fd = record_to_fd or {}
        self.all_generators = all_generators or {}
        self.current_generator = current_generator
        self.level88_map = level88_map or {}
        self.expr_trans = NativeExpressionTranslator(var_types)
        self.evaluate_count = 0
        self.evaluate_subject = None   # set when EVALUATE node is seen
        self.call_counter = 0

    def _is_variable(self, name: str) -> bool:
        base = re.split(r'\(', name)[0].strip()
        return base in self.var_types

    def _get_var_type(self, name: str, default: str = "String") -> str:
        base = re.split(r'\(', name)[0].strip()
        return self.var_types.get(base, default)

    def translate_statement(self, node) -> str:
        props = node.properties if hasattr(node, "properties") else node.get("properties", {})
        stype = props.get("statement_type", "").upper()
        
        if stype == "MOVE":
            src = props.get("source", "")
            # Support both new 'targets' list and legacy 'target' string
            raw_tgt = props.get("targets") or props.get("target")
            targets = raw_tgt if isinstance(raw_tgt, list) else ([raw_tgt] if raw_tgt else [])
            
            assignments = []
            for tgt in targets:
                java_tgt = to_java_var(tgt)
                tgt_type = self._get_var_type(tgt, "String")
                
                src_upper = src.upper()
                if src_upper in ("SPACE", "SPACES"):
                    java_src = '""'
                elif src_upper in ("ZERO", "ZEROS", "ZEROES"):
                    java_src = 'BigDecimal.ZERO' if tgt_type == "BigDecimal" else "0"
                    tgt_pic = self.current_generator.var_pics.get(re.split(r'\(', tgt)[0].strip(), "") if self.current_generator else ""
                    if tgt_type == "String" and "Z" in tgt_pic.upper():
                        _, length, _, _ = NativeTypeMapper.parse_pic(tgt_pic)
                        java_src = f"String.format(\"%{length}d\", 0)"
                elif src_upper in ("HIGH-VALUE", "HIGH-VALUES"):
                    java_src = '"\\uFFFF"'
                elif src.startswith("'") or src.startswith('"'):
                    java_src = src
                elif re.match(r'^\d+(\.\d+)?$', src):
                    if tgt_type == "BigDecimal":
                        java_src = f"new BigDecimal(\"{src}\")"
                    elif tgt_type in ("Integer", "Long"):
                        java_src = src
                    else:
                        tgt_pic = self.current_generator.var_pics.get(re.split(r'\(', tgt)[0].strip(), "") if self.current_generator else ""
                        if tgt_type == "String" and "Z" in tgt_pic.upper():
                            _, length, _, _ = NativeTypeMapper.parse_pic(tgt_pic)
                            java_src = f"String.format(\"%{length}d\", {src})"
                        else:
                            java_src = f"\"{src}\""
                elif self._is_variable(src):
                    java_src = to_java_var(src)
                    src_type = self._get_var_type(src, "String")
                    if tgt_type == "BigDecimal" and src_type in ("Integer", "Long"):
                        java_src = f"BigDecimal.valueOf({java_src})"
                    elif tgt_type == "String" and src_type != "String":
                        tgt_pic = self.current_generator.var_pics.get(re.split(r'\(', tgt)[0].strip(), "") if self.current_generator else ""
                        if "Z" in tgt_pic.upper():
                            _, length, _, _ = NativeTypeMapper.parse_pic(tgt_pic)
                            java_src = f"String.format(\"%{length}d\", {java_src})"
                        else:
                            java_src = f"String.valueOf({java_src})"
                else:
                    java_src = f"\"{src}\""
                
                assignments.append(f"{java_tgt} = {java_src};")
            
            return "\n        ".join(assignments) if assignments else ""

        elif stype == "COMPUTE":
            tgt = props.get("target", "")
            expr = props.get("expression", "")
            java_tgt = to_java_var(tgt)
            tgt_type = self._get_var_type(tgt, "BigDecimal")
            
            translated_expr = self.expr_trans.translate(expr)
            return f"{java_tgt} = {translated_expr};"

        elif stype in ("ADD", "SUBTRACT", "MULTIPLY", "DIVIDE"):
            val = props.get("value", "")
            tgt = props.get("target", "")
            operand2 = props.get("operand2")
            
            java_tgt = to_java_var(tgt)
            tgt_type = self._get_var_type(tgt, "BigDecimal")
            
            if re.match(r'^\d+(\.\d+)?$', val):
                java_val = f"new BigDecimal(\"{val}\")" if tgt_type == "BigDecimal" else val
            else:
                java_val = to_java_var(val)
                val_type = self._get_var_type(val, "BigDecimal")
                if tgt_type == "BigDecimal" and val_type in ("Integer", "Long"):
                    java_val = f"BigDecimal.valueOf({java_val})"
            
            if operand2:
                java_op2 = to_java_var(operand2)
                op2_type = self._get_var_type(operand2, "BigDecimal")
                if tgt_type == "BigDecimal" and op2_type in ("Integer", "Long"):
                    java_op2 = f"BigDecimal.valueOf({java_op2})"
                
                if stype == "ADD":
                    return f"{java_tgt} = {java_val}.add({java_op2});" if tgt_type == "BigDecimal" else f"{java_tgt} = {java_val} + {java_op2};"
                elif stype == "SUBTRACT":
                    return f"{java_tgt} = {java_op2}.subtract({java_val});" if tgt_type == "BigDecimal" else f"{java_tgt} = {java_op2} - {java_val};"
                elif stype == "MULTIPLY":
                    return f"{java_tgt} = {java_val}.multiply({java_op2});" if tgt_type == "BigDecimal" else f"{java_tgt} = {java_val} * {java_op2};"
                else:
                    return f"{java_tgt} = {java_val}.divide({java_op2}, 2, RoundingMode.DOWN);" if tgt_type == "BigDecimal" else f"{java_tgt} = {java_val} / {java_op2};"
            else:
                if stype == "ADD":
                    return f"{java_tgt} = {java_tgt}.add({java_val});" if tgt_type == "BigDecimal" else f"{java_tgt} += {java_val};"
                elif stype == "SUBTRACT":
                    return f"{java_tgt} = {java_tgt}.subtract({java_val});" if tgt_type == "BigDecimal" else f"{java_tgt} -= {java_val};"
                elif stype == "MULTIPLY":
                    return f"{java_tgt} = {java_tgt}.multiply({java_val});" if tgt_type == "BigDecimal" else f"{java_tgt} *= {java_val};"
                else:
                    return f"{java_tgt} = {java_tgt}.divide({java_val}, 2, RoundingMode.DOWN);" if tgt_type == "BigDecimal" else f"{java_tgt} /= {java_val};"

        elif stype == "IF":
            cond = self._translate_condition(props.get("condition", ""))
            return f"if ({cond}) {{"
            
        elif stype == "ELSE":
            return "} else {"
            
        elif stype == "END-IF":
            return "}"

        elif stype == "PERFORM_UNTIL":
            cond = self._translate_condition(props.get("condition", ""))
            return f"while (!({cond})) {{"

        elif stype == "PERFORM_VARYING":
            idx = props.get("index", "")
            from_val = props.get("from_value", "1")
            by_val = props.get("by_value", "1")
            cond = self._translate_condition(props.get("condition", ""))
            java_idx = to_java_var(idx)
            idx_type = self.var_types.get(idx, "Integer")
            if idx_type == "BigDecimal":
                # Use BigDecimal loop variable
                by_expr = f"new BigDecimal(\"{by_val}\")" if re.match(r'^\d+(\.\d+)?$', by_val) else to_java_var(by_val)
                from_expr = f"new BigDecimal(\"{from_val}\")" if re.match(r'^\d+(\.\d+)?$', from_val) else to_java_var(from_val)
                return (f"for ({java_idx} = {from_expr}; !({cond}); "
                        f"{java_idx} = {java_idx}.add({by_expr})) {{")
            else:
                t_prim = "int" if idx_type == "Integer" else "long"
                return (f"for ({java_idx} = {from_val}; !({cond}); "
                        f"{java_idx} += {by_val}) {{")

        elif stype == "END-PERFORM":
            return "}"

        elif stype == "PERFORM":
            tgt = props.get("target", "")
            java_method = to_java_var(tgt)
            return f"{java_method}();"

        elif stype == "OPEN":
            open_calls = []
            targets = props.get("targets", [])
            if not targets and props.get("target"):
                targets = [props.get("target")]
                
            curr_mode = "INPUT"
            for t in targets:
                t_upper = t.upper()
                if t_upper in ("INPUT", "OUTPUT", "I-O", "EXTEND"):
                    curr_mode = t_upper
                    continue
                open_calls.append(f"open_{to_java_var(t)}();")
            return "\n        ".join(open_calls)

        elif stype == "CLOSE":
            close_calls = []
            targets = props.get("targets", [])
            if not targets and props.get("target"):
                targets = [props.get("target")]
                
            for t in targets:
                t_upper = t.upper()
                if t_upper in ("INPUT", "OUTPUT", "I-O", "EXTEND"):
                    # skip mode keywords if any slip in
                    continue
                close_calls.append(f"close_{to_java_var(t)}();")
            return "\n        ".join(close_calls)

        elif stype == "READ":
            tgt = props.get("target", "")
            into_target = props.get("into_target")
            at_end_nodes = props.get("at_end_nodes", [])
            not_at_end_nodes = props.get("not_at_end_nodes", [])
            
            java_tgt = to_java_var(tgt)
            
            rec_name = None
            for r, fd in self.record_to_fd.items():
                if fd.upper() == tgt.upper():
                    rec_name = r
                    break
            if not rec_name:
                rec_name = tgt
                
            lines = []
            if at_end_nodes or not_at_end_nodes or into_target:
                lines.append(f"if (!read_{java_tgt}()) {{")
                for node in at_end_nodes:
                    stmt_str = self.translate_statement(node)
                    if stmt_str:
                        lines.append(f"    {stmt_str}")
                lines.append("} else {")
                
                if into_target:
                    java_rec = to_java_var(rec_name)
                    java_into = to_java_var(into_target)
                    lines.append(f"    {java_into} = {java_rec};")
                    
                for node in not_at_end_nodes:
                    stmt_str = self.translate_statement(node)
                    if stmt_str:
                        lines.append(f"    {stmt_str}")
                lines.append("}")
                return "\n        ".join(lines)
            else:
                return f"read_{java_tgt}();"

        elif stype == "WRITE":
            tgt = props.get("target", "")
            from_source = props.get("from_source")
            matched_fd = self.record_to_fd.get(tgt)
            if not matched_fd:
                for assign in self.file_assigns:
                    logical = assign.get("logical_name", "")
                    if logical.replace("-FILE", "") in tgt or tgt.replace("-REC", "") in logical:
                        matched_fd = logical
                        break
            if not matched_fd:
                matched_fd = tgt
            java_tgt = to_java_var(matched_fd)
            
            lines = []
            if from_source:
                java_src = to_java_var(from_source)
                java_rec = to_java_var(tgt)
                lines.append(f"{java_rec} = {java_src};")
            lines.append(f"write_{java_tgt}();")
            return "\n        ".join(lines)

        elif stype == "GOBACK" or stype == "STOP RUN":
            return "return;"

        elif stype == "STRING":
            parts = props.get("parts", [])
            tgt = props.get("target", "")
            java_tgt = to_java_var(tgt)
            
            java_parts = []
            for part in parts:
                val = part.get("value", "")
                if val.startswith("'") or val.startswith('"'):
                    val_clean = val[1:-1].replace('"', '\\"')
                    java_parts.append(f"\"{val_clean}\"")
                elif val in self.var_types:
                    java_var = to_java_var(val)
                    var_type = self.var_types.get(val, "String")
                    if var_type == "String":
                        java_parts.append(java_var)
                    else:
                        java_parts.append(f"String.valueOf({java_var})")
                else:
                    java_parts.append(f"\"{val}\"")
            
            concat_expr = " + ".join(java_parts)
            return f"{java_tgt} = {concat_expr};"

        elif stype == "CALL":
            target = props.get("target", "")
            arguments = props.get("arguments", [])
            
            def get_flat_vars(prog_gen, arg_names):
                flat = []
                for arg in arg_names:
                    arg_upper = arg.upper()
                    if arg_upper in prog_gen.group_fields:
                        for child in prog_gen.group_fields[arg_upper]:
                            flat.append(child)
                    else:
                        flat.append(arg)
                return flat

            if not self.current_generator:
                return f"// CALL translation error: current_generator not set"

            caller_vars = get_flat_vars(self.current_generator, arguments)
            is_dynamic = target in self.var_types
            
            if is_dynamic:
                java_var = to_java_var(target)
                lines = []
                lines.append(f"String targetProg_{java_var} = {java_var}.trim().toUpperCase();")
                first = True
                for other_prog_name, other_gen in self.all_generators.items():
                    if other_prog_name == self.current_generator.program_name:
                        continue
                    cond = "if" if first else "else if"
                    first = False
                    lines.append(f"{cond} (targetProg_{java_var}.equals(\"{other_prog_name.upper()}\")) {{")
                    call_lines = self._generate_call_block(other_prog_name, other_gen, caller_vars)
                    for cl in call_lines:
                        lines.append(f"    {cl}")
                    lines.append("}")
                return "\n        ".join(lines)
            else:
                target_upper = target.upper()
                if target_upper in self.all_generators:
                    other_gen = self.all_generators[target_upper]
                    call_lines = self._generate_call_block(target_upper, other_gen, caller_vars)
                    return "\n        ".join(call_lines)
                else:
                    return f"// Call to unknown program: {target}"

        elif stype == "EVALUATE":
            self.evaluate_count = 0
            self.evaluate_subject = props.get("subject", None)
            return None  # emit nothing; WHEN handlers generate the if/else chain

        elif stype == "WHEN":
            self.evaluate_count += 1
            cond = props.get("condition", "")
            cond_upper = cond.upper().strip()
            if cond_upper == "OTHER":
                return "} else {"

            subject = self.evaluate_subject
            if subject:
                # Type-aware subject == cond comparison
                subj_java = to_java_var(subject) if subject in self.var_types else subject
                subj_type = self.var_types.get(subject, "String")
                cond_stripped = cond.strip().strip("'\"")
                if subj_type == "BigDecimal":
                    r_val = (f"new BigDecimal(\"{cond_stripped}\")"
                             if re.match(r'^\d+(\.\d+)?$', cond_stripped)
                             else to_java_var(cond_stripped))
                    java_cond = f"{subj_java}.compareTo({r_val}) == 0"
                elif subj_type in ("Integer", "Long"):
                    java_cond = f"{subj_java} == {cond_stripped}"
                else:
                    java_cond = f"Objects.equals({subj_java}, \"{cond_stripped}\")"
            else:
                java_cond = self._translate_condition(cond)

            if self.evaluate_count == 1:
                return f"if ({java_cond}) {{"
            else:
                return f"}} else if ({java_cond}) {{"

        elif stype == "END-EVALUATE":
            return "}"

        elif stype == "DISPLAY":
            operands = props.get("operands", [])
            if not operands:
                return 'System.out.println("");'
            parts = []
            for op in operands:
                val = op.get("value", "")
                op_type = op.get("type", "variable")
                if op_type == "literal":
                    clean = val.replace('"', '\\"')
                    parts.append(f"\"{clean}\"")
                else:
                    v_type = self._get_var_type(val)
                    jv = to_java_var(val)
                    if v_type == "String":
                        parts.append(jv)
                    else:
                        parts.append(f"String.valueOf({jv})")
            concat = ' + " " + '.join(parts) if len(parts) > 1 else parts[0]
            return f"System.out.println({concat});"

        return f"// Unsupported statement: {stype}"

    def _translate_subscripts(self, expr: str) -> str:
        pattern = r'(?<![A-Za-z0-9_-])([A-Za-z0-9_-]+)\s*\(\s*([^()]+)\s*\)'
        def repl(match):
            var_name = to_java_var(match.group(1))
            idx = match.group(2).strip()
            for v in self.var_types.keys():
                idx = re.sub(r'\b' + re.escape(v) + r'\b', to_java_var(v), idx)
            if idx.isdigit():
                return f"{var_name}[{int(idx) - 1}]"
            return f"{var_name}[{idx} - 1]"
        
        old = ""
        while old != expr:
            old = expr
            expr = re.sub(pattern, repl, expr)
        return expr

    def _translate_condition(self, cond: str) -> str:
        """Translate a COBOL condition string to Java boolean expression."""
        cond = self._translate_subscripts(cond)
        # Resolve Level-88 conditions
        for cond_name in self.level88_map.keys():
            pattern = r'(?<![A-Za-z0-9_-])' + re.escape(cond_name) + r'(?![A-Za-z0-9_-])'
            method_call = to_java_method(cond_name) + "()"
            cond = re.sub(pattern, method_call, cond, flags=re.IGNORECASE)

        cond = cond.replace("=", "==").replace("<>", "!=")
        for v in self.var_types.keys():
            cond = re.sub(r'\b' + re.escape(v) + r'\b', to_java_var(v), cond)
        for v, t in self.var_types.items():
            jv = to_java_var(v)
            if t == "BigDecimal":
                pattern = r'\b' + re.escape(jv) + r'(\[[^\]]+\])?\s*(==|!=|>|<|>=|<=)\s*([A-Za-z0-9_\-\.]+)\b'
                def repl_bd(match, _jv=jv):
                    sub = match.group(1) or ""
                    op = match.group(2)
                    right = match.group(3)
                    r_val = f"new BigDecimal(\"{right}\")" if re.match(r'^\d+(\.\d+)?$', right) else right
                    map_ops = {"==": "== 0", "!=": "!= 0", ">": "> 0", "<": "< 0", ">=": ">= 0", "<=": "<= 0"}
                    return f"{_jv}{sub}.compareTo({r_val}) {map_ops.get(op, op)}"
                cond = re.sub(pattern, repl_bd, cond)
            elif t == "String":
                pattern = r'\b' + re.escape(jv) + r'(\[[^\]]+\])?\s*(==|!=)\s*(\"[^\"]*\"|\'[^\']*\'|[A-Za-z0-9_\-\.]+)'
                def repl_str(match, _jv=jv):
                    sub = match.group(1) or ""
                    op = match.group(2)
                    right = match.group(3)
                    if right.startswith("'") or right.startswith('"'):
                        right = f"\"{right[1:-1]}\""
                    else:
                        right = to_java_var(right)
                    return f"{_jv}{sub}.equals({right})" if op == "==" else f"!{_jv}{sub}.equals({right})"
                cond = re.sub(pattern, repl_str, cond)
        return cond

    def _generate_call_block(self, target_name: str, target_gen, caller_vars: list) -> list:
        self.call_counter += 1
        suffix = f"_{self.call_counter}"
        target_vars = []
        for arg in target_gen.using_args:
            arg_upper = arg.upper()
            if arg_upper in target_gen.group_fields:
                for child in target_gen.group_fields[arg_upper]:
                    target_vars.append(child)
            else:
                target_vars.append(arg)
                
        java_class = to_java_class(target_name)
        var_name = to_java_var(target_name) + suffix
        
        lines = []
        lines.append(f"{java_class} {var_name} = new {java_class}();")
        
        for i, c_var in enumerate(caller_vars):
            if i < len(target_vars):
                t_var = target_vars[i]
                c_jvar = to_java_var(c_var)
                t_jvar = to_java_var(t_var)
                lines.append(f"{var_name}.{t_jvar} = {c_jvar};")
                
        lines.append(f"{var_name}.execute();")
        
        for i, c_var in enumerate(caller_vars):
            if i < len(target_vars):
                t_var = target_vars[i]
                c_jvar = to_java_var(c_var)
                t_jvar = to_java_var(t_var)
                lines.append(f"{c_jvar} = {var_name}.{t_jvar};")
                
        return lines

class NativeFileIOGenerator:
    @staticmethod
    def generate_io_methods(fd_name: str, assign_path: str, is_input: bool, record_fields: list) -> str:
        java_fd = to_java_var(fd_name)
        
        offsets = []
        curr = 0
        for f_name, pic in record_fields:
            _, length, _, _ = NativeTypeMapper.parse_pic(pic)
            offsets.append((f_name, curr, curr + length))
            curr += length

        lines = []
        if is_input:
            lines.append(f"    private BufferedReader {java_fd}_reader;")
            lines.append(f"    private void open_{java_fd}() {{")
            lines.append(f"        try {{")
            lines.append(f"            {java_fd}_reader = Files.newBufferedReader(Paths.get(\"{assign_path}\"));")
            lines.append(f"        }} catch (IOException e) {{")
            lines.append(f"            throw new RuntimeException(e);")
            lines.append(f"        }}")
            lines.append(f"    }}")
            lines.append("")
            lines.append(f"    private boolean read_{java_fd}() {{")
            lines.append(f"        try {{")
            lines.append(f"            String line = {java_fd}_reader.readLine();")
            lines.append(f"            if (line == null) {{")
            lines.append(f"                return false;")
            lines.append(f"            }} else {{")
            for f_name, start, end in offsets:
                java_var = to_java_var(f_name)
                pic = [p for n, p in record_fields if n == f_name][0]
                java_type = NativeTypeMapper.get_java_type(pic)
                
                lines.append(f"                if (line.length() >= {end}) {{")
                lines.append(f"                    String val = line.substring({start}, {end}).trim();")
                if java_type == "BigDecimal":
                    scale = NativeTypeMapper.parse_pic(pic)[2]
                    signed = NativeTypeMapper.parse_pic(pic)[3]
                    if signed:
                        lines.append(f"                    {java_var} = parseSigned(val, {scale});")
                    else:
                        lines.append(f"                    {java_var} = val.isEmpty() ? BigDecimal.ZERO : new BigDecimal(val).movePointLeft({scale});")
                elif java_type in ("Integer", "Long"):
                    signed = NativeTypeMapper.parse_pic(pic)[3]
                    t_cast = "int" if java_type == "Integer" else "long"
                    if signed:
                        lines.append(f"                    {java_var} = ({t_cast}) parseSignedLong(val);")
                    else:
                        parse_call = "Integer.parseInt(val)" if java_type == "Integer" else "Long.parseLong(val)"
                        zero_val = "0" if java_type == "Integer" else "0L"
                        lines.append(f"                    {java_var} = val.isEmpty() ? {zero_val} : {parse_call};")
                else:
                    lines.append(f"                    {java_var} = val;")
                lines.append(f"                }}")
            lines.append(f"            }}")
            lines.append(f"            return true;")
            lines.append(f"        }} catch (IOException e) {{")
            lines.append(f"            throw new RuntimeException(e);")
            lines.append(f"        }}")
            lines.append(f"    }}")
            lines.append("")
            lines.append(f"    private void close_{java_fd}() {{")
            lines.append(f"        try {{")
            lines.append(f"            if ({java_fd}_reader != null) {java_fd}_reader.close();")
            lines.append(f"        }} catch (IOException e) {{")
            lines.append(f"            throw new RuntimeException(e);")
            lines.append(f"        }}")
            lines.append(f"    }}")
        else:
            lines.append(f"    private BufferedWriter {java_fd}_writer;")
            lines.append(f"    private void open_{java_fd}() {{")
            lines.append(f"        try {{")
            lines.append(f"            Files.createDirectories(Paths.get(\"{assign_path}\").getParent());")
            lines.append(f"            {java_fd}_writer = Files.newBufferedWriter(Paths.get(\"{assign_path}\"));")
            lines.append(f"        }} catch (IOException e) {{")
            lines.append(f"            throw new RuntimeException(e);")
            lines.append(f"        }}")
            lines.append(f"    }}")
            lines.append("")
            lines.append(f"    private void write_{java_fd}() {{")
            lines.append(f"        try {{")
            format_parts = []
            vars_list = []
            for f_name, pic in record_fields:
                _, length, scale, signed = NativeTypeMapper.parse_pic(pic)
                java_var = to_java_var(f_name)
                java_type = NativeTypeMapper.get_java_type(pic)
                
                if java_type == "BigDecimal":
                    if signed:
                        format_parts.append("%s")
                        vars_list.append(f"formatSigned({java_var}.movePointRight({scale}).setScale(0, RoundingMode.DOWN).longValue(), {length}, true)")
                    else:
                        format_parts.append(f"%0{length}d")
                        vars_list.append(f"{java_var}.movePointRight({scale}).setScale(0, RoundingMode.DOWN).longValue()")
                elif java_type in ("Integer", "Long"):
                    if signed:
                        format_parts.append("%s")
                        vars_list.append(f"formatSigned({java_var}, {length}, true)")
                    else:
                        format_parts.append(f"%0{length}d")
                        vars_list.append(java_var)
                else:
                    format_parts.append(f"%-{length}s")
                    vars_list.append(f"({java_var} == null ? \"\" : {java_var})")
            
            format_str = "".join(format_parts)
            lines.append(f"            String line = String.format(\"{format_str}\", {', '.join(vars_list)});")
            lines.append(f"            {java_fd}_writer.write(line.stripTrailing());")
            lines.append(f"            {java_fd}_writer.write(\"\\n\");")
            lines.append(f"        }} catch (IOException e) {{")
            lines.append(f"            throw new RuntimeException(e);")
            lines.append(f"        }}")
            lines.append(f"    }}")
            lines.append("")
            lines.append(f"    private void close_{java_fd}() {{")
            lines.append(f"        try {{")
            lines.append(f"            if ({java_fd}_writer != null) {java_fd}_writer.close();")
            lines.append(f"        }} catch (IOException e) {{")
            lines.append(f"            throw new RuntimeException(e);")
            lines.append(f"        }}")
            lines.append(f"    }}")
            
        return "\n".join(lines)

class NativeProgramGenerator:
    def __init__(self, program_name: str, ir_nodes: list, file_assigns: list = None):
        self.program_name = program_name
        self.ir_nodes = ir_nodes
        self.file_assigns = file_assigns or []
        
        self.var_types = {}
        self.var_pics = {}
        self.fd_fields = {}
        self.record_to_fd = {}
        self.group_fields = {}
        self.using_args = []
        # level88_map: {condition_name: (parent_name, [values])}
        self.level88_map = {}
        # occurs_map: {array_var_name: (size, elem_java_type)}
        self.occurs_map = {}
        self._build_mappings()

    def _build_mappings(self):
        sorted_nodes = sorted(self.ir_nodes, key=lambda n: n.source_line)
        
        # Populate using_args
        for n in sorted_nodes:
            if n.kind == "DIVISION" and n.properties.get("name") == "PROCEDURE":
                self.using_args = n.properties.get("using_args", [])
                break

        last_non88 = None   # track parent of 88 conditions
        for n in sorted_nodes:
            props = n.properties
            kind = n.kind
            if kind in ("VARIABLE", "DATA_ITEM"):
                name = props.get("name", "")
                pic = props.get("picture", "")
                usage = props.get("usage", "")
                level = props.get("level", 1)
                if level == 88:
                    # Level-88 condition: map to parent
                    values = props.get("condition_values", [])
                    parent = last_non88 if last_non88 else ""
                    self.level88_map[name] = (parent, values)
                else:
                    if name:
                        last_non88 = name
                    if name and pic:
                        self.var_types[name] = NativeTypeMapper.get_java_type(pic, usage)
                        self.var_pics[name] = pic
                    # OCCURS table
                    occurs = props.get("occurs", 0)
                    if name and occurs and pic:
                        elem_type = NativeTypeMapper.get_java_type(pic, usage)
                        self.occurs_map[name] = (int(occurs), elem_type)

        # Populate group_fields
        current_group = None
        for n in sorted_nodes:
            if n.kind in ("VARIABLE", "DATA_ITEM"):
                name = n.properties.get("name", "")
                level = n.properties.get("level", 1)
                is_group = n.properties.get("is_group", False)
                if level == 1:
                    if is_group:
                        current_group = name.upper()
                        self.group_fields[current_group] = []
                    else:
                        current_group = None
                elif level > 1 and current_group:
                    self.group_fields[current_group].append(name)

        in_file_section = False
        file_records = []
        curr_record_fields = []
        record_names = []
        
        for n in sorted_nodes:
            props = n.properties
            kind = n.kind
            if kind == "SECTION":
                sec_name = props.get("name", "").upper()
                if sec_name == "FILE":
                    in_file_section = True
                elif sec_name == "WORKING-STORAGE":
                    in_file_section = False
                    if curr_record_fields:
                        file_records.append(curr_record_fields)
                        curr_record_fields = []
                        
            elif in_file_section and kind in ("VARIABLE", "DATA_ITEM"):
                name = props.get("name", "")
                level = props.get("level", 1)
                pic = props.get("picture", "")
                
                if level == 1:
                    if curr_record_fields:
                        file_records.append(curr_record_fields)
                    curr_record_fields = []
                    record_names.append(name)
                    if pic:
                        curr_record_fields.append((name, pic))
                elif level > 1 and name and pic:
                    curr_record_fields.append((name, pic))
                    
        if curr_record_fields:
            file_records.append(curr_record_fields)

        for i, assign in enumerate(self.file_assigns):
            logical = assign.get("logical_name", "")
            if i < len(file_records):
                self.fd_fields[logical] = file_records[i]
                if i < len(record_names):
                    self.record_to_fd[record_names[i]] = logical
            else:
                self.fd_fields[logical] = []

    def _get_var_line(self, var_name: str) -> int:
        for n in self.ir_nodes:
            if n.kind in ("VARIABLE", "DATA_ITEM") and n.properties.get("name") == var_name:
                return n.source_line
        return 9999

    def generate_class_source(self, all_generators: dict = None) -> str:
        class_name = to_java_class(self.program_name)
        
        lines = []
        lines.append("package com.systema.modernized.native_gen;")
        lines.append("")
        lines.append("import java.io.BufferedReader;")
        lines.append("import java.io.BufferedWriter;")
        lines.append("import java.io.IOException;")
        lines.append("import java.math.BigDecimal;")
        lines.append("import java.math.RoundingMode;")
        lines.append("import java.nio.file.Files;")
        lines.append("import java.nio.file.Paths;")
        lines.append("import java.util.Objects;")
        lines.append("")
        lines.append(f"public class {class_name} {{")
        lines.append("")
        
        for v, java_type in self.var_types.items():
            if v in self.occurs_map:
                continue
            java_var = to_java_var(v)
            initial_val = None
            for n in self.ir_nodes:
                if n.kind in ("VARIABLE", "DATA_ITEM") and n.properties.get("name") == v:
                    initial_val = n.properties.get("value")
                    break
            
            if initial_val is not None:
                initial_val = str(initial_val).strip()
                if initial_val.upper() in ("ZERO", "ZEROS", "ZEROES"):
                    if java_type == "BigDecimal":
                        lines.append(f"    public BigDecimal {java_var} = BigDecimal.ZERO;")
                    elif java_type in ("Integer", "Long"):
                        t_prim = "int" if java_type == "Integer" else "long"
                        lines.append(f"    public {t_prim} {java_var} = 0;")
                    else:
                        lines.append(f"    public String {java_var} = \"0\";")
                elif initial_val.upper() in ("SPACE", "SPACES"):
                    lines.append(f"    public String {java_var} = \"\";")
                else:
                    if (initial_val.startswith("'") and initial_val.endswith("'")) or \
                       (initial_val.startswith('"') and initial_val.endswith('"')):
                        initial_val = initial_val[1:-1]
                    
                    if java_type == "BigDecimal":
                        lines.append(f"    public BigDecimal {java_var} = new BigDecimal(\"{initial_val}\");")
                    elif java_type in ("Integer", "Long"):
                        cleaned_val = re.sub(r'[^\d\-]', '', initial_val)
                        if not cleaned_val:
                            cleaned_val = "0"
                        t_prim = "int" if java_type == "Integer" else "long"
                        lines.append(f"    public {t_prim} {java_var} = {cleaned_val};")
                    else:
                        lines.append(f"    public String {java_var} = \"{initial_val}\";")
            else:
                if java_type == "BigDecimal":
                    lines.append(f"    public BigDecimal {java_var} = BigDecimal.ZERO;")
                elif java_type == "Integer":
                    lines.append(f"    public int {java_var} = 0;")
                elif java_type == "Long":
                    lines.append(f"    public long {java_var} = 0L;")
                else:
                    lines.append(f"    public String {java_var} = \"\";")
        
        # Emit OCCURS array fields (skip scalars already emitted above)
        for arr_name, (arr_size, elem_type) in self.occurs_map.items():
            java_arr = to_java_var(arr_name)
            if elem_type == "BigDecimal":
                lines.append(f"    public BigDecimal[] {java_arr} = new BigDecimal[{arr_size}];")
                lines.append(f"    {{  // initialise array elements")
                lines.append(f"        java.util.Arrays.fill({java_arr}, BigDecimal.ZERO);")
                lines.append(f"    }}")
            elif elem_type == "Integer":
                lines.append(f"    public int[] {java_arr} = new int[{arr_size}];")
            elif elem_type == "Long":
                lines.append(f"    public long[] {java_arr} = new long[{arr_size}];")
            else:
                lines.append(f"    public String[] {java_arr} = new String[{arr_size}];")
                lines.append(f"    {{  // initialise array elements")
                lines.append(f"        java.util.Arrays.fill({java_arr}, \"\");")
                lines.append(f"    }}")

        # Emit level-88 boolean helpers
        for cond_name, (parent_name, values) in self.level88_map.items():
            if not parent_name:
                continue
            method_name = to_java_method(cond_name)
            parent_java = to_java_var(parent_name)
            parent_type = self.var_types.get(parent_name, "String")
            if parent_type == "BigDecimal":
                conds = " || ".join(
                    f"{parent_java}.compareTo(new BigDecimal(\"{v}\")) == 0" for v in values
                )
            elif parent_type in ("Integer", "Long"):
                conds = " || ".join(f"{parent_java} == {v}" for v in values)
            else:
                conds = " || ".join(f'Objects.equals({parent_java}, "{v}")' for v in values)
            lines.append(f"    public boolean {method_name}() {{ return {conds}; }}")

        lines.append("")
        
        for assign in self.file_assigns:
            logical = assign.get("logical_name", "")
            path = assign.get("assign_path", "")
            is_input = is_input_file(logical, path)
            if logical not in self.fd_fields or not self.fd_fields[logical]:
                continue
            fields = self.fd_fields[logical]
            
            lines.append(NativeFileIOGenerator.generate_io_methods(logical, path, is_input, fields))
            lines.append("")

        proc_nodes = [n for n in self.ir_nodes if n.kind == "STATEMENT"]
        
        paragraphs = {}
        curr_p = None
        in_procedure = False
        
        for n in self.ir_nodes:
            kind = n.kind
            if kind == "DIVISION" and n.properties.get("name") == "PROCEDURE":
                in_procedure = True
                continue
            if in_procedure:
                if kind in ("PARAGRAPH", "SECTION"):
                    curr_p = to_java_var(n.properties.get("name", ""))
                    paragraphs[curr_p] = []
                elif kind == "STATEMENT":
                    if curr_p is None:
                        curr_p = "main_process"
                        paragraphs[curr_p] = []
                    paragraphs[curr_p].append(n)

        first_p = None
        in_procedure = False
        for n in self.ir_nodes:
            if n.kind == "DIVISION" and n.properties.get("name") == "PROCEDURE":
                in_procedure = True
                continue
            if in_procedure and n.kind in ("PARAGRAPH", "SECTION"):
                first_p = to_java_var(n.properties.get("name", ""))
                break
        if not first_p:
            first_p = "main_process"

        stmt_trans = NativeStatementTranslator(self.var_types, self.file_assigns, self.record_to_fd, all_generators=all_generators, current_generator=self, level88_map=self.level88_map)
        
        lines.append("    public void execute() {")
        lines.append(f"        {first_p}();")
        lines.append("    }")
        lines.append("")
        
        for p_name, stmts in paragraphs.items():
            lines.append(f"    private void {p_name}() {{")
            skip_loop = False
            for s in stmts:
                props = s.properties if hasattr(s, "properties") else s.get("properties", {})
                stype = props.get("statement_type", "").upper()
                
                if stype in ("PERFORM_UNTIL", "PERFORM_VARYING"):
                    java_stmt = stmt_trans.translate_statement(s)
                    lines.append(f"        {java_stmt}")
                    continue
                
                if stype == "END-PERFORM":
                    lines.append("        }")
                    continue
                    
                java_stmt = stmt_trans.translate_statement(s)
                if java_stmt and not java_stmt.startswith("// Unsupported statement:"):
                    lines.append(f"        {java_stmt}")
            lines.append("    }")
            lines.append("")
            
        lines.append("    public static void main(String[] args) {")
        lines.append(f"        new {class_name}().execute();")
        lines.append("    }")
        lines.append("")
        lines.append("    private static String formatSigned(long value, int length, boolean signed) {")
        lines.append("        if (!signed) {")
        lines.append("            return String.format(\"%0\" + length + \"d\", Math.abs(value));")
        lines.append("        }")
        lines.append("        if (value >= 0) {")
        lines.append("            return String.format(\"%0\" + length + \"d\", value);")
        lines.append("        } else {")
        lines.append("            long absVal = Math.abs(value);")
        lines.append("            String absStr = String.format(\"%0\" + length + \"d\", absVal);")
        lines.append("            char lastChar = absStr.charAt(absStr.length() - 1);")
        lines.append("            char signChar;")
        lines.append("            switch (lastChar) {")
        lines.append("                case '0': signChar = 'p'; break;")
        lines.append("                case '1': signChar = 'q'; break;")
        lines.append("                case '2': signChar = 'r'; break;")
        lines.append("                case '3': signChar = 's'; break;")
        lines.append("                case '4': signChar = 't'; break;")
        lines.append("                case '5': signChar = 'u'; break;")
        lines.append("                case '6': signChar = 'v'; break;")
        lines.append("                case '7': signChar = 'w'; break;")
        lines.append("                case '8': signChar = 'x'; break;")
        lines.append("                case '9': signChar = 'y'; break;")
        lines.append("                default: signChar = lastChar;")
        lines.append("            }")
        lines.append("            return absStr.substring(0, absStr.length() - 1) + signChar;")
        lines.append("        }")
        lines.append("    }")
        lines.append("")
        lines.append("    private static BigDecimal parseSigned(String val, int scale) {")
        lines.append("        if (val == null || val.trim().isEmpty()) {")
        lines.append("            return BigDecimal.ZERO;")
        lines.append("        }")
        lines.append("        val = val.trim();")
        lines.append("        char last = val.charAt(val.length() - 1);")
        lines.append("        boolean negative = false;")
        lines.append("        char replacement = last;")
        lines.append("        if (last >= 'p' && last <= 'y') {")
        lines.append("            negative = true;")
        lines.append("            replacement = (char) ('0' + (last - 'p'));")
        lines.append("        }")
        lines.append("        String cleanVal = val.substring(0, val.length() - 1) + replacement;")
        lines.append("        BigDecimal bd = new BigDecimal(cleanVal);")
        lines.append("        if (negative) {")
        lines.append("            bd = bd.negate();")
        lines.append("        }")
        lines.append("        return bd.movePointLeft(scale);")
        lines.append("    }")
        lines.append("")
        lines.append("    private static long parseSignedLong(String val) {")
        lines.append("        if (val == null || val.trim().isEmpty()) {")
        lines.append("            return 0;")
        lines.append("        }")
        lines.append("        val = val.trim();")
        lines.append("        char last = val.charAt(val.length() - 1);")
        lines.append("        boolean negative = false;")
        lines.append("        char replacement = last;")
        lines.append("        if (last >= 'p' && last <= 'y') {")
        lines.append("            negative = true;")
        lines.append("            replacement = (char) ('0' + (last - 'p'));")
        lines.append("        }")
        lines.append("        String cleanVal = val.substring(0, val.length() - 1) + replacement;")
        lines.append("        long l = Long.parseLong(cleanVal);")
        lines.append("        return negative ? -l : l;")
        lines.append("    }")
        lines.append("")
        lines.append("}")
        return "\n".join(lines)
