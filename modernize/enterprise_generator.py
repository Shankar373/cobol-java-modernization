import os
import re
import shutil

def to_java_class(name: str) -> str:
    if not name:
        return ""
    # Remove extension and clean up
    base = os.path.splitext(name)[0]
    cleaned = re.sub(r'[^a-zA-Z0-9]', '', base)
    return cleaned.capitalize()

def to_java_var(name: str) -> str:
    if not name:
        return ""
    cleaned = re.sub(r'[^a-zA-Z0-9]', '', name)
    if not cleaned:
        return "var"
def resolve_primary_io_files(model: dict) -> dict:
    """
    Deterministically resolve primary batch input and output files from model metadata.
    Handles both nested and flat representations of file_assigns and file_ops.
    Rules:
      - Primary input: file opened for input (is_input=True), not INDEXED/RELATIVE,
        not written internally by another step, not in work/temp directories.
      - Primary output: file opened for output (is_output=True), not INDEXED/RELATIVE,
        not consumed internally as input by another step, not in work/temp directories.
    """
    file_assigns = (model or {}).get("file_assigns") or {}
    file_ops = (model or {}).get("file_ops") or {}
    
    registry = {}
    
    def _posix(p):
        return (p or "").replace("\\", "/")

    def _register(logical_name, assign_path, organization, src):
        if not logical_name and not assign_path:
            return
        key = (assign_path or logical_name).replace("\\", "/").lower()
        if key not in registry:
            registry[key] = {
                "logical_name": logical_name,
                "assign_path": assign_path,
                "organization": organization,
                "base_name": os.path.basename(assign_path) if assign_path else logical_name,
                "is_input": False,
                "is_output": False,
                "srcs": []
            }
        entry = registry[key]
        if organization and not entry["organization"]:
            entry["organization"] = organization
        if logical_name and not entry["logical_name"]:
            entry["logical_name"] = logical_name
        if assign_path and not entry["assign_path"]:
            entry["assign_path"] = assign_path
        if src:
            entry["srcs"].append(src)

    def _update_ops(logical_name, is_in, is_out):
        matched = False
        ln_clean = logical_name.upper()
        for entry in registry.values():
            if entry["logical_name"].upper() == ln_clean or entry["base_name"].upper() == ln_clean:
                if is_in: entry["is_input"] = True
                if is_out: entry["is_output"] = True
                matched = True
        if not matched:
            key = logical_name.lower()
            registry[key] = {
                "logical_name": logical_name,
                "assign_path": logical_name,
                "organization": "",
                "base_name": logical_name,
                "is_input": is_in,
                "is_output": is_out,
                "srcs": []
            }

    # 1. Ingest file_assigns
    if isinstance(file_assigns, dict):
        for src_or_ln, val in file_assigns.items():
            if isinstance(val, list):
                src = src_or_ln
                for a in val:
                    if isinstance(a, dict):
                        ln = a.get("logical_name") or ""
                        ap = a.get("assign_path") or ""
                        org = a.get("organization") or ""
                        _register(ln, ap, org, src)
            elif isinstance(val, dict):
                ln = src_or_ln
                ap = val.get("assign_path") or ""
                org = val.get("organization") or ""
                _register(ln, ap, org, None)
            elif isinstance(val, str):
                ln = src_or_ln
                ap = val
                _register(ln, ap, "", None)
    elif isinstance(file_assigns, list):
        for a in file_assigns:
            if isinstance(a, dict):
                ln = a.get("logical_name") or ""
                ap = a.get("assign_path") or ""
                org = a.get("organization") or ""
                _register(ln, ap, org, None)

    # 2. Ingest file_ops
    if isinstance(file_ops, dict):
        for src_or_ln, ops_or_mode in file_ops.items():
            if isinstance(ops_or_mode, dict):
                src = src_or_ln
                for ln, info in ops_or_mode.items():
                    if isinstance(info, dict):
                        is_in = bool(info.get("is_input"))
                        is_out = bool(info.get("is_output"))
                        open_modes = [m.upper() for m in info.get("open_modes", [])]
                        if "INPUT" in open_modes: is_in = True
                        if "I-O" in open_modes: is_in = True; is_out = True
                        if "OUTPUT" in open_modes or "EXTEND" in open_modes: is_out = True
                        _update_ops(ln, is_in, is_out)
                    elif isinstance(info, str):
                        m = info.upper()
                        _update_ops(ln, m in ("INPUT", "I-O"), m in ("OUTPUT", "EXTEND", "I-O"))
            elif isinstance(ops_or_mode, str):
                ln = src_or_ln
                m = ops_or_mode.upper()
                _update_ops(ln, m in ("INPUT", "I-O"), m in ("OUTPUT", "EXTEND", "I-O"))

    # Fallback heuristic if no explicit operations recorded
    for entry in registry.values():
        if not entry["is_input"] and not entry["is_output"]:
            p_upper = entry["assign_path"].upper()
            ln_upper = entry["logical_name"].upper()
            if "IN" in p_upper.split("/") or "INPUT" in ln_upper or "IN" in ln_upper:
                entry["is_input"] = True
            if "OUT" in p_upper.split("/") or "OUTPUT" in ln_upper or "OUT" in ln_upper or "REPT" in ln_upper:
                entry["is_output"] = True

    # 3. Filter candidates
    candidates_in = []
    candidates_out = []
    for entry in registry.values():
        org = str(entry["organization"]).upper()
        parts = [p.lower() for p in _posix(entry["assign_path"]).split("/")]
        is_indexed = org in ("INDEXED", "RELATIVE")
        is_work = "work" in parts or "tmp" in parts or "temp" in parts
        if entry["is_input"] and not is_indexed and not is_work:
            candidates_in.append(entry)
        if entry["is_output"] and not is_indexed and not is_work:
            candidates_out.append(entry)

    def _rank_in(e):
        score = 0
        if not e["is_output"]:
            score += 100
        parts = [p.lower() for p in _posix(e["assign_path"]).split("/")]
        if any(p in ("in", "input", "inputs", "source", "source_data", "datasets") for p in parts):
            score += 50
        if "IN" in e["logical_name"].upper():
            score += 20
        return score

    def _rank_out(e):
        score = 0
        if not e["is_input"]:
            score += 100
        parts = [p.lower() for p in _posix(e["assign_path"]).split("/")]
        fn = parts[-1] if parts else ""
        if any(w in fn for w in ("report", "rept", "rpt", "summary", "eod")):
            score += 50
        if fn.endswith((".txt", ".rpt", ".csv")):
            score += 30
        if "REPT" in e["logical_name"].upper() or "REPORT" in e["logical_name"].upper():
            score += 20
        if any(p in ("out", "output", "outputs", "reports") for p in parts):
            score += 10
        return score

    candidates_in.sort(key=_rank_in, reverse=True)
    candidates_out.sort(key=_rank_out, reverse=True)

    return {
        "all_files": registry,
        "primary_input": candidates_in[0] if candidates_in else None,
        "primary_output": candidates_out[0] if candidates_out else None,
        "candidate_inputs": candidates_in,
        "candidate_outputs": candidates_out,
        "inputs": [e["logical_name"] for e in candidates_in],
        "outputs": [e["logical_name"] for e in candidates_out]
    }


class EnterpriseApplicationGenerator:
    def resolve_primary_io_files(self) -> dict:
        return resolve_primary_io_files(self.model)

    def __init__(self, repo_path: str, model: dict, native_class_name: str, has_db_evidence: bool = False, has_rest_evidence: bool = False):
        self.repo_path = os.path.abspath(repo_path) if repo_path else ""
        self.model = model
        self.native_class_name = native_class_name
        self.has_db_evidence = has_db_evidence
        self.has_rest_evidence = has_rest_evidence

    def generate_project(self, dest_dir: str):
        shutil.rmtree(dest_dir, ignore_errors=True)
        
        src_main = os.path.join(dest_dir, "src", "main")
        java_base = os.path.join(src_main, "java", "com", "systema", "modernized")
        resources_dir = os.path.join(src_main, "resources")
        
        os.makedirs(java_base, exist_ok=True)
        os.makedirs(os.path.join(java_base, "domain"), exist_ok=True)
        os.makedirs(os.path.join(java_base, "repository"), exist_ok=True)
        os.makedirs(os.path.join(java_base, "service"), exist_ok=True)
        os.makedirs(os.path.join(java_base, "batch"), exist_ok=True)
        os.makedirs(os.path.join(java_base, "controller"), exist_ok=True)
        os.makedirs(resources_dir, exist_ok=True)

        parsed_models = self.model.get("parsed_models", {})
        
        # 1. JPA Repository / Entities (evidence-driven)
        is_jpa_applicable = self.has_db_evidence
        for mname, fields in parsed_models.items():
            self._write_jpa_entity(java_base, mname, fields, is_jpa=is_jpa_applicable)
            if is_jpa_applicable:
                self._write_jpa_repository(java_base, mname)

        # 2. REST Controller (evidence-driven)
        if self.has_rest_evidence:
            self._write_rest_controller(java_base)

        # 3. Spring Batch (evidence-driven)
        has_batch = self._check_batch_evidence()
        if has_batch:
            self._write_spring_batch_config(java_base)

        # 4. Project Metadata
        self._write_pom_xml(dest_dir, is_jpa_applicable)
        self._write_properties(resources_dir, is_jpa_applicable)
        self._write_main_application(java_base)
        self._write_spring_context_helper(java_base)
        self._write_db2_error_mapper(java_base)
        self._write_jcl_execution_context(java_base)
        self._write_cobol_format_helper(java_base)
        self._write_cobol_ref(java_base)
        self._write_db2_verify(java_base)
        self._write_cics_program_registry(java_base)
        self._write_cics_transaction_context(java_base)
        
        # Copy runtime helper files
        runtime_dest = os.path.join(java_base, "runtime")
        os.makedirs(runtime_dest, exist_ok=True)
        runtime_src = os.path.join(os.path.dirname(__file__), "java_helpers", "src", "main", "java", "com", "systema", "modernized", "runtime")
        if os.path.isdir(runtime_src):
            for f in os.listdir(runtime_src):
                if f.endswith(".java"):
                    shutil.copy2(os.path.join(runtime_src, f), os.path.join(runtime_dest, f))

        # Copy MockSqlService.java: generated SQL programs call
        # MockSqlService.initialize() in their main(). The class already has a
        # safe no-op path when PGHOST is set (real PostgreSQL) or REAL_DB2_MODE=1.
        # It must be present for Maven compilation regardless of whether a
        # mock_db.yaml is present in the repository.
        mss_src = os.path.join(os.path.dirname(__file__), "java_helpers", "src", "main", "java", "com", "systema", "modernized", "MockSqlService.java")
        if os.path.exists(mss_src):
            shutil.copy2(mss_src, os.path.join(java_base, "MockSqlService.java"))

        self._write_dockerfile(dest_dir)

    def _check_batch_evidence(self) -> bool:
        # If there are file assignments or file operations, batch is applicable
        file_assigns = self.model.get("file_assigns") or {}
        file_ops = self.model.get("file_ops") or {}
        return len(file_assigns) > 0 or len(file_ops) > 0

    def _write_jpa_entity(self, java_base: str, mname: str, fields: list, is_jpa: bool):
        cname = to_java_class(mname)
        # BUG-G007: sanitize table/column names — hyphens are invalid in SQL identifiers
        table_name = mname.lower().replace("-", "_")
        lines = []
        lines.append("package com.systema.modernized.domain;")
        lines.append("")
        if is_jpa:
            lines.append("import jakarta.persistence.*;")
            lines.append("import java.math.BigDecimal;")
            lines.append("")
            lines.append("@Entity")
            lines.append(f"@Table(name = \"{table_name}\")")
        else:
            lines.append("import java.math.BigDecimal;")
            lines.append("")
            
        lines.append(f"public class {cname} {{")
        lines.append("")
        
        # Identity field for JPA
        if is_jpa:
            lines.append("    @Id")
            lines.append("    @GeneratedValue(strategy = GenerationType.IDENTITY)")
            lines.append("    private Long internalJpaId;")
            lines.append("")
            
        for f in fields:
            camel = f.get("camel_name", "")
            jtype = f.get("type", "String")
            if not camel:
                continue
            if is_jpa:
                # BUG-G007: use sanitized raw_name as column name
                raw_name = f.get("raw_name", camel)
                col_name = raw_name.lower().replace("-", "_")
                lines.append(f"    @Column(name = \"{col_name}\")")
            lines.append(f"    private {jtype} {camel};")
            lines.append("")

        lines.append("")
        
        # Getters and setters
        if is_jpa:
            lines.append("    public Long getInternalJpaId() { return internalJpaId; }")
            lines.append("    public void setInternalJpaId(Long id) { this.internalJpaId = id; }")
            lines.append("")
            
        for f in fields:
            camel = f.get("camel_name", "")
            jtype = f.get("type", "String")
            if not camel:
                continue
            cap = camel[0].upper() + camel[1:]
            lines.append(f"    public {jtype} get{cap}() {{ return {camel}; }}")
            lines.append(f"    public void set{cap}({jtype} val) {{ this.{camel} = val; }}")
            lines.append("")
            
        lines.append("}")
        
        path = os.path.join(java_base, "domain", f"{cname}.java")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def _write_jpa_repository(self, java_base: str, mname: str):
        cname = to_java_class(mname)
        lines = []
        lines.append("package com.systema.modernized.repository;")
        lines.append("")
        lines.append(f"import com.systema.modernized.domain.{cname};")
        lines.append("import org.springframework.data.jpa.repository.JpaRepository;")
        lines.append("import org.springframework.stereotype.Repository;")
        lines.append("")
        lines.append("@Repository")
        lines.append(f"public interface {cname}Repository extends JpaRepository<{cname}, Long> {{")
        lines.append("}")
        
        path = os.path.join(java_base, "repository", f"{cname}Repository.java")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def _write_rest_controller(self, java_base: str):
        lines = []
        lines.append("package com.systema.modernized.controller;")
        lines.append("")
        lines.append("import org.springframework.web.bind.annotation.*;")
        lines.append("import org.springframework.http.ResponseEntity;")
        lines.append("")
        lines.append("@RestController")
        lines.append("@RequestMapping(\"/api\")")
        lines.append("public class ModernizedRestController {")
        lines.append("")
        lines.append("    @GetMapping(\"/status\")")
        lines.append("    public ResponseEntity<String> getStatus() {")
        lines.append("        return ResponseEntity.ok(\"Modernized service running successfully\");")
        lines.append("    }")
        lines.append("}")
        
        path = os.path.join(java_base, "controller", "ModernizedRestController.java")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def _write_spring_batch_config(self, java_base: str):
        io_info = self.resolve_primary_io_files()
        file_assigns = self.model.get("file_assigns") or {}
        file_ops    = self.model.get("file_ops")    or {}
        input_logical_names  = []  # list of (logical_name, assign_path)
        output_logical_names = []  # list of (logical_name, assign_path)

        def _resolve_assign_path(logical: str, src_key: str = None) -> str:
            if src_key and isinstance(file_assigns, dict):
                src_entry = file_assigns.get(src_key)
                if isinstance(src_entry, list):
                    for a in src_entry:
                        if isinstance(a, dict) and a.get("logical_name") == logical:
                            return a.get("assign_path", "")
            if isinstance(file_assigns, dict):
                if logical in file_assigns:
                    v = file_assigns[logical]
                    if isinstance(v, str):
                        return v
                    elif isinstance(v, dict):
                        return v.get("assign_path", "")
                for _, v in file_assigns.items():
                    if isinstance(v, list):
                        for a in v:
                            if isinstance(a, dict) and a.get("logical_name") == logical:
                                return a.get("assign_path", "")
            elif isinstance(file_assigns, list):
                for a in file_assigns:
                    if isinstance(a, dict) and a.get("logical_name") == logical:
                        return a.get("assign_path", "")
            return ""

        for src, ops in file_ops.items():
            if isinstance(ops, dict):
                for logical_name, info in ops.items():
                    ap = _resolve_assign_path(logical_name, src)
                    is_in = False
                    is_out = False
                    if isinstance(info, dict):
                        is_in = bool(info.get("is_input"))
                        is_out = bool(info.get("is_output"))
                    elif isinstance(info, str):
                        is_in = info.upper() in ("INPUT", "I-O")
                        is_out = info.upper() in ("OUTPUT", "EXTEND", "I-O")
                    if is_in:
                        input_logical_names.append((logical_name, ap))
                    elif is_out:
                        output_logical_names.append((logical_name, ap))
            elif isinstance(ops, str):
                logical_name = src
                ap = _resolve_assign_path(logical_name)
                if ops.upper() in ("INPUT", "I-O"):
                    input_logical_names.append((logical_name, ap))
                elif ops.upper() in ("OUTPUT", "EXTEND", "I-O"):
                    output_logical_names.append((logical_name, ap))

        lines = []
        lines.append("package com.systema.modernized.batch;")
        lines.append("")
        lines.append("import org.springframework.batch.core.Job;")
        lines.append("import org.springframework.batch.core.Step;")
        lines.append("import org.springframework.batch.core.job.builder.JobBuilder;")
        lines.append("import org.springframework.batch.core.repository.JobRepository;")
        lines.append("import org.springframework.batch.core.step.builder.StepBuilder;")
        lines.append("import org.springframework.beans.factory.annotation.Value;")
        lines.append("import org.springframework.context.annotation.Bean;")
        lines.append("import org.springframework.context.annotation.Configuration;")
        lines.append("import org.springframework.transaction.PlatformTransactionManager;")
        lines.append("")
        lines.append("@Configuration")
        lines.append("public class SpringBatchConfig {")
        lines.append("")
        # Inject batch input/output paths from Spring properties / CLI args
        lines.append("    /** Absolute path to the batch input file (passed via --app.batch.input=<path>). */")
        lines.append("    @Value(\"${app.batch.input:}\")")
        lines.append("    private String batchInputPath;")
        lines.append("")
        lines.append("    /** Relative output file name (passed via --app.report.output=<name>). */")
        lines.append("    @Value(\"${app.report.output:}\")")
        lines.append("    private String batchOutputPath;")
        lines.append("")
        lines.append("    @Bean")
        lines.append("    public Job modernizedJob(JobRepository jobRepository, Step step1) {")
        lines.append("        return new JobBuilder(\"modernizedJob\", jobRepository)")
        lines.append("                .start(step1)")
        lines.append("                .build();")
        lines.append("    }")
        lines.append("")
        lines.append("    @Bean")
        lines.append("    public Step step1(JobRepository jobRepository, PlatformTransactionManager transactionManager, org.springframework.jdbc.core.JdbcTemplate jdbcTemplate) {")
        lines.append(f"        String entryClass = \"{to_java_class(self.native_class_name)}\";")
        lines.append("        return new StepBuilder(\"step1\", jobRepository)")
        lines.append("                .tasklet((contribution, chunkContext) -> {")
        lines.append("                    com.systema.modernized.SpringContextHelper.jdbcTemplate = jdbcTemplate;")
        lines.append("                    com.systema.modernized.SpringContextHelper.transactionManager = transactionManager;")
        # Wire input file path into JclExecutionContext for primary input DD
        primary_in = io_info.get("primary_input")
        if primary_in:
            lines.append("                    // Wire batch input path into JCL DD assignments for primary batch input.")
            lines.append("                    if (batchInputPath != null && !batchInputPath.isEmpty()) {")
            ln = primary_in["logical_name"]
            base = primary_in.get("base_name") or ""
            lines.append(f'                        com.systema.modernized.JclExecutionContext.setDdAssignment("{ln}", batchInputPath);')
            if base and base.upper() != ln.upper():
                lines.append(f'                        com.systema.modernized.JclExecutionContext.setDdAssignment("{base}", batchInputPath);')
            lines.append("                    }")
        elif input_logical_names:
            lines.append("                    if (batchInputPath != null && !batchInputPath.isEmpty()) {")
            for ln, ap in input_logical_names:
                lines.append(f'                        com.systema.modernized.JclExecutionContext.setDdAssignment("{ln}", batchInputPath);')
                if ap:
                    import os as _os
                    base = _os.path.basename(ap)
                    if base and base.upper() != ln.upper():
                        lines.append(f'                        com.systema.modernized.JclExecutionContext.setDdAssignment("{base}", batchInputPath);')
            lines.append("                    }")

        # Wire output file path into JclExecutionContext for primary report DD
        primary_out = io_info.get("primary_output")
        if primary_out:
            lines.append("                    // Wire batch output path into JCL DD assignments for primary report output.")
            lines.append("                    if (batchOutputPath != null && !batchOutputPath.isEmpty()) {")
            ln = primary_out["logical_name"]
            base = primary_out.get("base_name") or ""
            lines.append(f'                        com.systema.modernized.JclExecutionContext.setDdAssignment("{ln}", batchOutputPath);')
            if base and base.upper() != ln.upper():
                lines.append(f'                        com.systema.modernized.JclExecutionContext.setDdAssignment("{base}", batchOutputPath);')
            lines.append("                    }")
        elif output_logical_names:
            lines.append("                    if (batchOutputPath != null && !batchOutputPath.isEmpty()) {")
            for ln, ap in output_logical_names:
                lines.append(f'                        com.systema.modernized.JclExecutionContext.setDdAssignment("{ln}", batchOutputPath);')
                if ap:
                    import os as _os
                    base = _os.path.basename(ap)
                    if base and base.upper() != ln.upper():
                        lines.append(f'                        com.systema.modernized.JclExecutionContext.setDdAssignment("{base}", batchOutputPath);')
            lines.append("                    }")
        lines.append("                    try {")
        lines.append(f"                        new com.systema.modernized.native_gen.{to_java_class(self.native_class_name)}().execute();")
        lines.append(f"                    }} catch (com.systema.modernized.native_gen.{to_java_class(self.native_class_name)}.StopRunException e) {{")
        lines.append("                        // Clean exit via STOP RUN")
        lines.append("                    } catch (Exception e) {")
        lines.append("                        throw new RuntimeException(e);")
        lines.append("                    }")
        lines.append("                    return org.springframework.batch.repeat.RepeatStatus.FINISHED;")
        lines.append("                }, transactionManager)")
        lines.append("                .build();")
        lines.append("    }")
        lines.append("}")

        path = os.path.join(java_base, "batch", "SpringBatchConfig.java")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def _write_pom_xml(self, dest_dir: str, is_jpa: bool):
        lines = []
        lines.append("<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
        lines.append("<project xmlns=\"http://maven.apache.org/POM/4.0.0\"")
        lines.append("         xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"")
        lines.append("         xsi:schemaLocation=\"http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd\">")
        lines.append("    <modelVersion>4.0.0</modelVersion>")
        lines.append("    <parent>")
        lines.append("        <groupId>org.springframework.boot</groupId>")
        lines.append("        <artifactId>spring-boot-starter-parent</artifactId>")
        lines.append("        <version>3.2.2</version>")
        lines.append("        <relativePath/>")
        lines.append("    </parent>")
        lines.append("    <groupId>com.systema</groupId>")
        lines.append("    <artifactId>modernized</artifactId>")
        lines.append("    <version>1.0.0</version>")
        lines.append("    <name>modernized</name>")
        lines.append("    <description>Enterprise Modernized Spring Boot App</description>")
        lines.append("    <properties>")
        lines.append("        <java.version>17</java.version>")
        lines.append("    </properties>")
        lines.append("    <dependencies>")
        
        lines.append("        <dependency>")
        lines.append("            <groupId>org.springframework.boot</groupId>")
        lines.append("            <artifactId>spring-boot-starter-web</artifactId>")
        lines.append("        </dependency>")
            
        lines.append("        <dependency>")
        lines.append("            <groupId>org.springframework.boot</groupId>")
        lines.append("            <artifactId>spring-boot-starter-data-jpa</artifactId>")
        lines.append("        </dependency>")
        lines.append("        <dependency>")
        lines.append("            <groupId>com.h2database</groupId>")
        lines.append("            <artifactId>h2</artifactId>")
        lines.append("        </dependency>")
        lines.append("        <dependency>")
        lines.append("            <groupId>org.postgresql</groupId>")
        lines.append("            <artifactId>postgresql</artifactId>")
        lines.append("            <scope>runtime</scope>")
        lines.append("        </dependency>")
            
        if self._check_batch_evidence():
            lines.append("        <dependency>")
            lines.append("            <groupId>org.springframework.boot</groupId>")
            lines.append("            <artifactId>spring-boot-starter-batch</artifactId>")
            lines.append("        </dependency>")
            
        lines.append("        <dependency>")
        lines.append("            <groupId>org.springframework.boot</groupId>")
        lines.append("            <artifactId>spring-boot-starter-test</artifactId>")
        lines.append("            <scope>test</scope>")
        lines.append("        </dependency>")
        lines.append("    </dependencies>")
        lines.append("    <build>")
        lines.append("        <plugins>")
        lines.append("            <plugin>")
        lines.append("                <groupId>org.springframework.boot</groupId>")
        lines.append("                <artifactId>spring-boot-maven-plugin</artifactId>")
        lines.append("            </plugin>")
        lines.append("        </plugins>")
        lines.append("    </build>")
        lines.append("    <profiles>")
        lines.append("        <profile>")
        lines.append("            <id>db2</id>")
        lines.append("            <dependencies>")
        lines.append("                <dependency>")
        lines.append("                    <groupId>com.ibm.db2</groupId>")
        lines.append("                    <artifactId>jcc</artifactId>")
        lines.append("                    <version>11.5.8.0</version>")
        lines.append("                    <scope>runtime</scope>")
        lines.append("                </dependency>")
        lines.append("            </dependencies>")
        lines.append("        </profile>")
        lines.append("    </profiles>")
        lines.append("</project>")
        
        path = os.path.join(dest_dir, "pom.xml")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def _write_properties(self, resources_dir: str, is_jpa: bool):
        lines = []
        lines.append("spring.application.name=modernized")
        
        url_var = "SPRING_DATASOURCE_URL"
        driver_var = "SPRING_DATASOURCE_DRIVER"
        user_var = "SPRING_DATASOURCE_USERNAME"
        pass_var = "SPRING_DATASOURCE_PASSWORD"
        dialect_var = "SPRING_JPA_DIALECT"

        # PostgreSQL default configuration values (Track B target)
        pg_url_default = "jdbc:postgresql://localhost:5432/postgres"
        pg_driver_default = "org.postgresql.Driver"
        pg_user_default = "postgres"
        pg_pass_default = "postgres"
        pg_dialect_default = "org.hibernate.dialect.PostgreSQLDialect"

        # Check if legacy DB2 or H2 overrides are present in environment variables
        if os.environ.get("REAL_DB2_MODE") == "1":
            url_var = "DB2_URL"
            driver_var = "DB2_DRIVER"
            user_var = "DB2_USERNAME"
            pass_var = "DB2_PASSWORD"
            dialect_var = "DB2_DIALECT"
            db2_url = os.environ.get("DB2_URL") or "jdbc:db2://localhost:50000/SAMPLE"
            pg_url_default = db2_url
            pg_driver_default = "com.ibm.db2.jcc.DB2Driver"
            pg_user_default = os.environ.get("DB2_USERNAME") or "db2user"
            pg_pass_default = os.environ.get("DB2_PASSWORD") or ""
            pg_dialect_default = "org.hibernate.dialect.DB2Dialect"
        elif not os.environ.get("SPRING_DATASOURCE_URL"):
            # Fallback to local H2 in-memory test database for automated test suites if no PG is running
            pg_url_default = "jdbc:h2:mem:testdb;MODE=PostgreSQL;DATABASE_TO_LOWER=TRUE;DEFAULT_NULL_ORDERING=HIGH;DB_CLOSE_DELAY=-1;DB_CLOSE_ON_EXIT=FALSE"
            pg_driver_default = "org.h2.Driver"
            pg_user_default = "sa"
            pg_pass_default = ""
            pg_dialect_default = "org.hibernate.dialect.H2Dialect"

        lines.append(f"spring.datasource.url=${{{url_var}:{pg_url_default}}}")
        lines.append(f"spring.datasource.driverClassName=${{{driver_var}:{pg_driver_default}}}")
        lines.append(f"spring.datasource.username=${{{user_var}:{pg_user_default}}}")
        lines.append(f"spring.datasource.password=${{{pass_var}:{pg_pass_default}}}")
        
        # Handle schema mapping in application.properties if configured
        db_schema = os.environ.get("DB2_SCHEMA") or os.environ.get("SPRING_DATASOURCE_SCHEMA")
        if db_schema:
            lines.append(f"spring.datasource.hikari.schema={db_schema}")
            if is_jpa:
                lines.append(f"spring.jpa.properties.hibernate.default_schema={db_schema}")

        if is_jpa:
            lines.append(f"spring.jpa.database-platform=${{{dialect_var}:{pg_dialect_default}}}")
            lines.append("spring.hibernate.ddl-auto=update")
            
        if self._check_batch_evidence():
            lines.append("spring.batch.job.enabled=true")
            lines.append("spring.batch.jdbc.initialize-schema=always")
            # Placeholder properties consumed by SpringBatchConfig @Value injection.
            # The actual values are supplied at runtime via --app.batch.input=<path>
            # and --app.report.output=<name> command-line arguments.
            lines.append("app.batch.input=")
            lines.append("app.report.output=")

        path = os.path.join(resources_dir, "application.properties")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def _write_main_application(self, java_base: str):
        lines = []
        lines.append("package com.systema.modernized;")
        lines.append("")
        lines.append("import org.springframework.boot.SpringApplication;")
        lines.append("import org.springframework.boot.autoconfigure.SpringBootApplication;")
        lines.append("")
        lines.append("@SpringBootApplication")
        lines.append("public class ModernizedApplication {")
        lines.append("    public static void main(String[] args) {")
        lines.append("        SpringApplication.run(ModernizedApplication.class, args);")
        lines.append("    }")
        lines.append("}")
        
        path = os.path.join(java_base, "ModernizedApplication.java")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def _write_spring_context_helper(self, java_base: str):
        lines = []
        lines.append("package com.systema.modernized;")
        lines.append("")
        lines.append("import org.springframework.jdbc.core.JdbcTemplate;")
        lines.append("import org.springframework.transaction.PlatformTransactionManager;")
        lines.append("")
        lines.append("public class SpringContextHelper {")
        lines.append("    public static JdbcTemplate jdbcTemplate;")
        lines.append("    public static PlatformTransactionManager transactionManager;")
        lines.append("}")
        
        path = os.path.join(java_base, "SpringContextHelper.java")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def _write_db2_error_mapper(self, java_base: str):
        mapper_src = """package com.systema.modernized;
public class Db2ErrorMapper {
    public static int getSqlCode(Exception e) {
        if (e instanceof org.springframework.dao.EmptyResultDataAccessException) {
            return 100;
        }
        Throwable cause = e.getCause();
        if (cause instanceof java.sql.SQLException) {
            java.sql.SQLException sqle = (java.sql.SQLException) cause;
            String state = sqle.getSQLState();
            if ("23505".equals(state)) return -803; // duplicate key
            if ("42P01".equals(state) || "42S02".equals(state)) return -204; // table undefined
            if ("42703".equals(state) || "42S22".equals(state)) return -206; // column undefined
            int code = sqle.getErrorCode();
            return code != 0 ? -Math.abs(code) : -1;
        }
        return -1;
    }
    
    public static String getSqlState(Exception e) {
        if (e instanceof org.springframework.dao.EmptyResultDataAccessException) {
            return "02000";
        }
        Throwable cause = e.getCause();
        if (cause instanceof java.sql.SQLException) {
            java.sql.SQLException sqle = (java.sql.SQLException) cause;
            String state = sqle.getSQLState();
            if ("42P01".equals(state) || "42S02".equals(state)) return "42704"; // table undefined
            if ("42703".equals(state) || "42S22".equals(state)) return "42704";
            return state != null ? state : "99999";
        }
        return "99999";
    }
}
"""
        path = os.path.join(java_base, "Db2ErrorMapper.java")
        with open(path, "w", encoding="utf-8") as f:
            f.write(mapper_src)

    def _write_jcl_execution_context(self, java_base: str):
        jcl_context_src = """package com.systema.modernized;
import java.util.HashMap;
import java.util.Map;
public class JclExecutionContext {
    private static final ThreadLocal<Map<String, String>> ddAssignments = ThreadLocal.withInitial(HashMap::new);
    private static final ThreadLocal<Map<String, String>> sysinData = ThreadLocal.withInitial(HashMap::new);
    private static final ThreadLocal<Map<String, Integer>> stepReturnCodes = ThreadLocal.withInitial(HashMap::new);
    
    public static void setDdAssignment(String ddName, String physicalPath) {
        ddAssignments.get().put(ddName.toUpperCase(), physicalPath);
    }
    
    public static String getDdAssignment(String ddName) {
        return ddAssignments.get().get(ddName.toUpperCase());
    }
    
    public static void setSysinData(String ddName, String data) {
        sysinData.get().put(ddName.toUpperCase(), data);
    }
    
    public static String getSysinData(String ddName) {
        return sysinData.get().get(ddName.toUpperCase());
    }
    
    public static void setStepReturnCode(String stepName, int rc) {
        stepReturnCodes.get().put(stepName.toUpperCase(), rc);
    }
    
    public static Integer getStepReturnCode(String stepName) {
        return stepReturnCodes.get().getOrDefault(stepName.toUpperCase(), 0);
    }
    
    public static boolean checkAnyStepCond(int code, String op) {
        for (int rc : stepReturnCodes.get().values()) {
            if (compareRc(code, op, rc)) {
                return true;
            }
        }
        return false;
    }
    
    public static boolean compareRc(int code, String op, int rc) {
        switch (op.toUpperCase()) {
            case "EQ": return code == rc;
            case "NE": return code != rc;
            case "GT": return code > rc;
            case "LT": return code < rc;
            case "GE": return code >= rc;
            case "LE": return code <= rc;
            default: return false;
        }
    }
    
    public static void clear() {
        ddAssignments.get().clear();
        sysinData.get().clear();
        stepReturnCodes.get().clear();
    }
}
"""
        path = os.path.join(java_base, "JclExecutionContext.java")
        with open(path, "w", encoding="utf-8") as f:
            f.write(jcl_context_src)

    def _write_cobol_format_helper(self, java_base: str):
        helper_path = os.path.join(os.path.dirname(__file__), "java_helpers", "CobolFormatHelper.java")
        with open(helper_path, "r", encoding="utf-8") as fh:
            src = fh.read()
        path = os.path.join(java_base, "CobolFormatHelper.java")
        with open(path, "w", encoding="utf-8") as f:
            f.write(src)

    def _write_cics_program_registry(self, java_base: str):
        registry_src = """package com.systema.modernized;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Supplier;
public class CicsProgramRegistry {
    private static final Map<String, Supplier<Object>> registry = new HashMap<>();
    public static void register(String name, Supplier<Object> supplier) {
        registry.put(name.toUpperCase(), supplier);
    }
    public static Object invoke(String name, String commarea) throws Exception {
        Supplier<Object> supplier = registry.get(name.toUpperCase());
        if (supplier == null) {
            try {
                String cleaned = name.replace("-", " ").replace("_", " ");
                String[] parts = cleaned.split("\\\\s+");
                StringBuilder sb = new StringBuilder();
                for (String p : parts) {
                    if (!p.isEmpty()) {
                        sb.append(p.substring(0, 1).toUpperCase());
                        sb.append(p.substring(1).toLowerCase());
                    }
                }
                String className = sb.toString();
                Class.forName("com.systema.modernized." + className);
                supplier = registry.get(name.toUpperCase());
            } catch (Exception e) {}
        }
        if (supplier == null) {
            throw new IllegalArgumentException("CICS_INVALID_PROGRAM: Program " + name + " not registered in CICS registry");
        }
        Object program = supplier.get();
        try {
            java.lang.reflect.Field field = program.getClass().getField("commarea");
            field.set(program, commarea);
        } catch (NoSuchFieldException e) {}
        program.getClass().getMethod("execute").invoke(program);
        try {
            java.lang.reflect.Field field = program.getClass().getField("commarea");
            return field.get(program);
        } catch (NoSuchFieldException e) {
            return commarea;
        }
    }
}
"""
        path = os.path.join(java_base, "CicsProgramRegistry.java")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(registry_src)

    def _write_cics_transaction_context(self, java_base: str):
        context_src = """package com.systema.modernized;
import java.util.HashMap;
import java.util.Map;
public class CicsTransactionContext {
    private static final Map<String, Object> session = new HashMap<>();
    private static final Map<String, Map<String, Object>> lastSendOptions = new HashMap<>();
    private static final Map<String, Map<String, Object>> lastReceiveOptions = new HashMap<>();
    
    public static void send(String map, String mapset, Object data) {
        send(map, mapset, data, new HashMap<>());
    }
    public static void send(String map, String mapset, Object data, Map<String, Object> options) {
        System.out.println("CICS SEND MAP: " + map + " MAPSET: " + mapset + " DATA: " + data + " OPTIONS: " + options);
        String key = mapset.toUpperCase() + "_" + map.toUpperCase();
        session.put(key + "_sent", data);
        lastSendOptions.put(key, options);
    }
    public static Object receive(String map, String mapset) {
        return receive(map, mapset, new HashMap<>());
    }
    public static Object receive(String map, String mapset, Map<String, Object> options) {
        System.out.println("CICS RECEIVE MAP: " + map + " MAPSET: " + mapset + " OPTIONS: " + options);
        String key = mapset.toUpperCase() + "_" + map.toUpperCase();
        lastReceiveOptions.put(key, options);
        return session.get(key + "_input");
    }
    public static void setSessionInput(String map, String mapset, Object data) {
        session.put(mapset.toUpperCase() + "_" + map.toUpperCase() + "_input", data);
    }
    public static Object getSessionSent(String map, String mapset) {
        return session.get(mapset.toUpperCase() + "_" + map.toUpperCase() + "_sent");
    }
    public static Object getSendOption(String map, String mapset, String optionName) {
        Map<String, Object> opts = lastSendOptions.get(mapset.toUpperCase() + "_" + map.toUpperCase());
        return opts != null ? opts.get(optionName.toLowerCase()) : null;
    }
    public static Object getReceiveOption(String map, String mapset, String optionName) {
        Map<String, Object> opts = lastReceiveOptions.get(mapset.toUpperCase() + "_" + map.toUpperCase());
        return opts != null ? opts.get(optionName.toLowerCase()) : null;
    }
    public static void cicsReturn() {
        System.out.println("CICS RETURN");
    }
    public static void clear() {
        session.clear();
        lastSendOptions.clear();
        lastReceiveOptions.clear();
    }
}
"""
        path = os.path.join(java_base, "CicsTransactionContext.java")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(context_src)

    def _write_cobol_ref(self, java_base: str):
        helper_path = os.path.join(os.path.dirname(__file__), "java_helpers", "CobolRef.java")
        if os.path.exists(helper_path):
            with open(helper_path, "r", encoding="utf-8") as fh:
                src = fh.read()
            path = os.path.join(java_base, "CobolRef.java")
            with open(path, "w", encoding="utf-8") as f:
                f.write(src)

    def _write_db2_verify(self, java_base: str):
        helper_path = os.path.join(os.path.dirname(__file__), "java_helpers", "Db2Verify.java")
        if os.path.exists(helper_path):
            with open(helper_path, "r", encoding="utf-8") as fh:
                src = fh.read()
            path = os.path.join(java_base, "Db2Verify.java")
            with open(path, "w", encoding="utf-8") as f:
                f.write(src)

    def _write_dockerfile(self, dest_dir: str):
        lines = []
        lines.append("FROM openjdk:17-jdk-alpine")
        lines.append("VOLUME /tmp")
        lines.append("COPY target/modernized-1.0.0.jar app.jar")
        lines.append("ENTRYPOINT [\"java\",\"-jar\",\"/app.jar\"]")
        
        path = os.path.join(dest_dir, "Dockerfile")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def analyze_topology(self) -> dict:
        """
        Analyse the discovered file-flow topology.
        Returns a dict with:
          - inputs: list of logical input file names
          - outputs: list of logical output file names
          - programs: list of discovered program IDs
          - flow_type: SINGLE_IO | MULTI_INPUT | MULTI_OUTPUT | MULTI_INDEPENDENT | COMPOSITE
          - gap: True if topology cannot be safely represented in generated Spring artifacts
          - gap_reason: MULTI_FILE_ARCHITECTURAL_GAP message or None
        """
        file_assigns = self.model.get("file_assigns") or {}
        file_ops = self.model.get("file_ops") or {}

        # Classify files by I/O mode
        inputs = [k for k, v in file_ops.items() if v in ("INPUT", "I-O")]
        outputs = [k for k, v in file_ops.items() if v in ("OUTPUT", "EXTEND", "I-O")]
        # Fall back to file_assigns keys if file_ops not available
        if not inputs and not outputs:
            inputs = list(file_assigns.keys())
            outputs = []

        programs = self.model.get("programs") or []

        # Determine flow type
        if len(inputs) <= 1 and len(outputs) <= 1:
            flow_type = "SINGLE_IO"
        elif len(inputs) > 1 and len(outputs) <= 1:
            flow_type = "MULTI_INPUT"
        elif len(inputs) <= 1 and len(outputs) > 1:
            flow_type = "MULTI_OUTPUT"
        elif len(programs) > 1 and (len(inputs) > 1 or len(outputs) > 1):
            flow_type = "COMPOSITE"
        else:
            flow_type = "MULTI_INDEPENDENT"

        # Gap check: if there are multiple independent programs each with their own
        # files but the model doesn't declare how they interconnect, flag a gap.
        gap = False
        gap_reason = None
        if len(programs) > 1 and not self.model.get("call_graph") and flow_type not in ("SINGLE_IO",):
            gap = True
            gap_reason = (
                "MULTI_FILE_ARCHITECTURAL_GAP: multiple programs discovered with multi-file "
                "topology but no call-graph provided — generated Spring Batch topology may be incomplete"
            )

        return {
            "inputs": inputs,
            "outputs": outputs,
            "programs": programs,
            "flow_type": flow_type,
            "gap": gap,
            "gap_reason": gap_reason,
        }

