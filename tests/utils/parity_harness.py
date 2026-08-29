import os
import shutil
import tempfile
import subprocess
import pytest
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

# Environment defaults
PARITY_RUNTIME = os.environ.get("PARITY_RUNTIME", "docker")
PARITY_JAVA_RUNTIME = os.environ.get("PARITY_JAVA_RUNTIME", "docker")
PARITY_GNUCOBOL_IMAGE = os.environ.get("PARITY_GNUCOBOL_IMAGE", "hurriedreformist/gnucobol:3.1-builder")
PARITY_JDK_IMAGE = os.environ.get("PARITY_JDK_IMAGE", "eclipse-temurin:17-jdk-noble")
PARITY_ALLOW_SKIP = os.environ.get("PARITY_ALLOW_SKIP", "false").lower() == "true"
PARITY_KEEP_ARTIFACTS_ON_FAILURE = os.environ.get("PARITY_KEEP_ARTIFACTS_ON_FAILURE", "true").lower() == "true"
PARITY_ARTIFACT_DIR = os.environ.get("PARITY_ARTIFACT_DIR", "artifacts/parity-failures")

@dataclass
class ParityFixture:
    name: str
    program_name: str
    cobol_code: str
    input_files: Dict[str, bytes] = field(default_factory=dict)
    stdin_bytes: bytes = b""
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    declared_outputs: List[str] = field(default_factory=list)  # Output files to verify

@dataclass
class ExecutionResult:
    rc: int
    stdout: bytes
    stderr: bytes
    files: Dict[str, bytes] = field(default_factory=dict)
    duration_seconds: float = 0.0
    termination_status: str = "normal"  # "normal" | "timeout" | "nonzero_exit" | "error"
    error_message: str = ""

@dataclass
class ParityMismatch:
    target: str  # "exit_code" | "stdout" | "stderr" | "file:<filename>"
    offset: int = -1
    cobol_val: bytes = b""
    java_val: bytes = b""
    cobol_hex: str = ""
    java_hex: str = ""
    explanation: str = ""

@dataclass
class ParityComparison:
    status: str  # "PASS" | "FAIL" | "SKIP"
    mismatches: List[ParityMismatch] = field(default_factory=list)
    skip_reason: str = ""

def run_cmd_bytes(cmd: List[str], stdin_bytes: bytes = None, timeout: int = 120) -> Tuple[int, bytes, bytes, str]:
    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE if stdin_bytes is not None else subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = proc.communicate(input=stdin_bytes, timeout=timeout)
        term = "normal"
        if proc.returncode != 0:
            term = "nonzero_exit"
        return proc.returncode, stdout, stderr, term
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        return -1, stdout, stderr, "timeout"
    except Exception as e:
        return -2, b"", str(e).encode("utf-8"), "error"

def check_docker_available() -> bool:
    try:
        res = subprocess.run(["docker", "info"], capture_output=True, timeout=10)
        return res.returncode == 0
    except Exception:
        return False

def check_docker_image_cached(image: str) -> bool:
    try:
        res = subprocess.run(["docker", "images", "-q", image], capture_output=True, text=True, timeout=10)
        return bool(res.stdout.strip())
    except Exception:
        return False

def run_cobol_baseline(fixture: ParityFixture, run_dir: str) -> ExecutionResult:
    # Write cobol source file
    src_file = os.path.join(run_dir, f"{fixture.program_name}.cob")
    with open(src_file, "wb") as f:
        f.write(fixture.cobol_code.encode("utf-8"))

    if PARITY_RUNTIME == "local":
        # Local fallback execution
        compile_cmd = ["cobc", "-x", "-std=default", "-fsign=ASCII", "-o", os.path.join(run_dir, "prog.exe"), src_file]
        rc, out, err, term = run_cmd_bytes(compile_cmd)
        if rc != 0:
            return ExecutionResult(rc, out, err, termination_status="error", error_message=f"GnuCOBOL compilation failed: {err.decode('utf-8', errors='replace')}")
        
        run_cmd = [os.path.join(run_dir, "prog.exe")] + fixture.args
        rc, out, err, term = run_cmd_bytes(run_cmd, stdin_bytes=fixture.stdin_bytes)
        
        # Read output files
        outputs = {}
        for f_name in fixture.declared_outputs:
            p_path = os.path.join(run_dir, f_name)
            if os.path.exists(p_path):
                with open(p_path, "rb") as f:
                    outputs[f_name] = f.read()
            else:
                outputs[f_name] = b""
        return ExecutionResult(rc, out, err, files=outputs, termination_status=term)
        
    else:
        # Docker canonical runtime execution
        if not check_docker_available():
            raise RuntimeError("Docker is not running, but PARITY_RUNTIME=docker is canonical.")
        if not check_docker_image_cached(PARITY_GNUCOBOL_IMAGE):
            raise RuntimeError(f"Required Docker image {PARITY_GNUCOBOL_IMAGE} is not cached.")

        # Mount run_dir to /run
        run_dir_abs = os.path.abspath(run_dir).replace("\\", "/")
        
        # Compile inside GnuCOBOL container
        inner_compile = f"cobc -x -std=default -fsign=ASCII -o /run/prog.exe /run/{fixture.program_name}.cob"
        compile_cmd = [
            "docker", "run", "--rm",
            "-v", f"{run_dir_abs}:/run",
            "-w", "/run",
            PARITY_GNUCOBOL_IMAGE,
            "sh", "-c", inner_compile
        ]
        rc, out, err, term = run_cmd_bytes(compile_cmd)
        if rc != 0:
            return ExecutionResult(rc, out, err, termination_status="error", error_message=f"Docker GnuCOBOL compilation failed: {err.decode('utf-8', errors='replace')}")

        # Stdin redirect inside docker execution
        with open(os.path.join(run_dir, "stdin.txt"), "wb") as f:
            f.write(fixture.stdin_bytes)

        inner_run = f"/run/prog.exe < /run/stdin.txt"
        run_cmd = [
            "docker", "run", "--rm",
            "-v", f"{run_dir_abs}:/run",
            "-w", "/run",
            PARITY_GNUCOBOL_IMAGE,
            "sh", "-c", inner_run
        ]
        rc, out, err, term = run_cmd_bytes(run_cmd)

        # Read output files
        outputs = {}
        for f_name in fixture.declared_outputs:
            p_path = os.path.join(run_dir, f_name)
            if os.path.exists(p_path):
                with open(p_path, "rb") as f:
                    outputs[f_name] = f.read()
            else:
                outputs[f_name] = b""
        return ExecutionResult(rc, out, err, files=outputs, termination_status=term)

def run_java_transpiled(fixture: ParityFixture, run_dir: str) -> ExecutionResult:
    # 1. Transpile COBOL source to Java source
    from modernize.lexer import CobolLexer
    from modernize.parser import CobolParser
    from modernize.native_generator import NativeProgramGenerator

    filename = f"{fixture.program_name}.cob"
    lexer = CobolLexer(filename)
    tokens = lexer.tokenize(fixture.cobol_code)
    parser = CobolParser(tokens, filename)
    ir = parser.parse()

    gen = NativeProgramGenerator(fixture.program_name, list(ir.nodes.values()))
    all_generators = {fixture.program_name.upper(): gen}
    def register_child_generators(g):
        for c_name, c_gen in g.child_generators.items():
            all_generators[c_name.upper()] = c_gen
            register_child_generators(c_gen)
    register_child_generators(gen)
    java_source = gen.generate_class_source(all_generators)

    # 2. Write Java source files and runtime helper dependencies to run_dir
    pkg_dir = os.path.join(run_dir, "com", "systema", "modernized", "native_gen")
    os.makedirs(pkg_dir, exist_ok=True)
    
    # Adjust assignments in generated Java to refer to absolute paths in temporary workspace
    adjusted_java_source = java_source
    if hasattr(gen, "file_assigns") and gen.file_assigns:
        for assign in gen.file_assigns:
            k = assign.get("physical_path") or assign.get("assign_path")
            if k:
                if PARITY_JAVA_RUNTIME == "docker":
                    target_path = f"/run/{k}"
                else:
                    target_path = os.path.abspath(os.path.join(run_dir, k)).replace("\\", "/")
                adjusted_java_source = adjusted_java_source.replace(f'"{k}"', f'"{target_path}"')

    src_file_path = os.path.join(pkg_dir, f"{fixture.program_name.capitalize()}.java")
    with open(src_file_path, "w", encoding="utf-8") as f:
        f.write(adjusted_java_source)

    jcl_context_dir = os.path.join(run_dir, "com", "systema", "modernized")
    os.makedirs(jcl_context_dir, exist_ok=True)

    # Write JclExecutionContext, CobolFormatHelper, CicsProgramRegistry, SpringContextHelper
    with open(os.path.join(jcl_context_dir, "JclExecutionContext.java"), "w", encoding="utf-8") as f:
        f.write("""package com.systema.modernized;
import java.util.HashMap;
import java.util.Map;
public class JclExecutionContext {
    private static final ThreadLocal<Map<String, String>> ddAssignments = ThreadLocal.withInitial(HashMap::new);
    private static final ThreadLocal<Map<String, String>> sysinData = ThreadLocal.withInitial(HashMap::new);
    private static final ThreadLocal<Map<String, Integer>> stepReturnCodes = ThreadLocal.withInitial(HashMap::new);
    public static void setDdAssignment(String ddName, String physicalPath) { ddAssignments.get().put(ddName.toUpperCase(), physicalPath); }
    public static String getDdAssignment(String ddName) { return ddAssignments.get().get(ddName.toUpperCase()); }
    public static void setSysinData(String ddName, String data) { sysinData.get().put(ddName.toUpperCase(), data); }
    public static String getSysinData(String ddName) { return sysinData.get().get(ddName.toUpperCase()); }
    public static void setStepReturnCode(String stepName, int rc) { stepReturnCodes.get().put(stepName.toUpperCase(), rc); }
    public static Integer getStepReturnCode(String stepName) { return stepReturnCodes.get().getOrDefault(stepName.toUpperCase(), 0); }
    public static boolean checkAnyStepCond(int code, String op) { return false; }
    public static boolean compareRc(int code, String op, int rc) { return false; }
    public static void clear() { ddAssignments.get().clear(); sysinData.get().clear(); stepReturnCodes.get().clear(); }
}""")

    with open(os.path.join(jcl_context_dir, "CicsProgramRegistry.java"), "w", encoding="utf-8") as f:
        f.write("""package com.systema.modernized;
public class CicsProgramRegistry {
    public static void register(String name, java.util.function.Supplier<Object> supplier) {}
    public static Object invoke(String name, String commarea) throws Exception { return commarea; }
}""")

    with open(os.path.join(jcl_context_dir, "SpringContextHelper.java"), "w", encoding="utf-8") as f:
        f.write("""package com.systema.modernized;
public class SpringContextHelper {
    public static class MockResultSet {
        public String getString(String c) { return null; }
        public String getString(int idx) { return null; }
    }
    public interface MockRowMapper<T> { T mapRow(MockResultSet rs, int r) throws Exception; }
    public static class MockJdbcTemplate {
        public void execute(String sql) {}
        public int update(String sql, Object... args) { return 0; }
    }
    public static MockJdbcTemplate jdbcTemplate = null;
}""")

    # Copy stable format and numeric runtime helpers
    helpers_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    format_helper_src = open(os.path.join(helpers_dir, "modernize", "java_helpers", "CobolFormatHelper.java"), "r", encoding="utf-8").read()
    with open(os.path.join(jcl_context_dir, "CobolFormatHelper.java"), "w", encoding="utf-8") as f:
        f.write(format_helper_src)

    runtime_dir = os.path.join(jcl_context_dir, "runtime")
    os.makedirs(runtime_dir, exist_ok=True)
    helpers_src_dir = os.path.join(helpers_dir, "modernize", "java_helpers", "src", "main", "java", "com", "systema", "modernized", "runtime")
    for f_name in os.listdir(helpers_src_dir):
        if f_name.endswith(".java"):
            src = open(os.path.join(helpers_src_dir, f_name), "r", encoding="utf-8").read()
            with open(os.path.join(runtime_dir, f_name), "w", encoding="utf-8") as f:
                f.write(src)

    if PARITY_JAVA_RUNTIME == "local":
        # Compile Java sources locally
        java_files = [os.path.join(runtime_dir, f) for f in os.listdir(runtime_dir) if f.endswith(".java")]
        compile_cmd = [
            "javac", "-cp", run_dir,
            os.path.join(jcl_context_dir, "JclExecutionContext.java"),
            os.path.join(jcl_context_dir, "CicsProgramRegistry.java"),
            os.path.join(jcl_context_dir, "SpringContextHelper.java"),
            os.path.join(jcl_context_dir, "CobolFormatHelper.java")
        ] + java_files + [src_file_path]
        rc, out, err, term = run_cmd_bytes(compile_cmd)
        if rc != 0:
            return ExecutionResult(rc, out, err, termination_status="error", error_message=f"Java compilation failed: {err.decode('utf-8', errors='replace')}")

        run_cmd = ["java", "-cp", run_dir, f"com.systema.modernized.native_gen.{fixture.program_name.capitalize()}"]
        rc, out, err, term = run_cmd_bytes(run_cmd, stdin_bytes=fixture.stdin_bytes)

        # Read output files
        outputs = {}
        for f_name in fixture.declared_outputs:
            p_path = os.path.join(run_dir, f_name)
            if os.path.exists(p_path):
                with open(p_path, "rb") as f:
                    outputs[f_name] = f.read()
            else:
                outputs[f_name] = b""
        return ExecutionResult(rc, out, err, files=outputs, termination_status=term)

    else:
        # Docker Temurin canonical runtimes execution
        if not check_docker_available():
            raise RuntimeError("Docker is not running, but PARITY_JAVA_RUNTIME=docker is canonical.")
        if not check_docker_image_cached(PARITY_JDK_IMAGE):
            raise RuntimeError(f"Required Docker image {PARITY_JDK_IMAGE} is not cached.")

        run_dir_abs = os.path.abspath(run_dir).replace("\\", "/")

        # Compile inside Docker
        inner_compile = (
            "javac -cp /run "
            "/run/com/systema/modernized/JclExecutionContext.java "
            "/run/com/systema/modernized/CicsProgramRegistry.java "
            "/run/com/systema/modernized/SpringContextHelper.java "
            "/run/com/systema/modernized/CobolFormatHelper.java "
            "/run/com/systema/modernized/runtime/*.java "
            f"/run/com/systema/modernized/native_gen/{fixture.program_name.capitalize()}.java"
        )
        compile_cmd = [
            "docker", "run", "--rm",
            "-v", f"{run_dir_abs}:/run",
            "-w", "/run",
            PARITY_JDK_IMAGE,
            "sh", "-c", inner_compile
        ]
        rc, out, err, term = run_cmd_bytes(compile_cmd)
        if rc != 0:
            return ExecutionResult(rc, out, err, termination_status="error", error_message=f"Docker Java compilation failed: {err.decode('utf-8', errors='replace')}")

        # Stdin redirect inside docker
        with open(os.path.join(run_dir, "stdin.txt"), "wb") as f:
            f.write(fixture.stdin_bytes)

        inner_run = f"java -cp /run com.systema.modernized.native_gen.{fixture.program_name.capitalize()} < /run/stdin.txt"
        run_cmd = [
            "docker", "run", "--rm",
            "-v", f"{run_dir_abs}:/run",
            "-w", "/run",
            PARITY_JDK_IMAGE,
            "sh", "-c", inner_run
        ]
        rc, out, err, term = run_cmd_bytes(run_cmd)

        # Read output files
        outputs = {}
        for f_name in fixture.declared_outputs:
            p_path = os.path.join(run_dir, f_name)
            if os.path.exists(p_path):
                with open(p_path, "rb") as f:
                    outputs[f_name] = f.read()
            else:
                outputs[f_name] = b""
        return ExecutionResult(rc, out, err, files=outputs, termination_status=term)

def compare_raw_bytes(target: str, cobol_bytes: bytes, java_bytes: bytes) -> ParityMismatch:
    if cobol_bytes == java_bytes:
        return None

    # Find first different byte offset
    offset = 0
    min_len = min(len(cobol_bytes), len(java_bytes))
    while offset < min_len and cobol_bytes[offset] == java_bytes[offset]:
        offset += 1

    # Hex rendering
    c_slice = cobol_bytes[max(0, offset - 8):min(len(cobol_bytes), offset + 8)]
    j_slice = java_bytes[max(0, offset - 8):min(len(java_bytes), offset + 8)]
    
    cobol_hex = c_slice.hex(" ")
    java_hex = j_slice.hex(" ")
    
    return ParityMismatch(
        target=target,
        offset=offset,
        cobol_val=c_slice,
        java_val=j_slice,
        cobol_hex=cobol_hex,
        java_hex=java_hex,
        explanation=f"Mismatch on target {target} at byte offset {offset}. COBOL length: {len(cobol_bytes)}, Java length: {len(java_bytes)}"
    )

def run_parity(fixture: ParityFixture) -> ParityComparison:
    # 1. Environment pre-validation
    docker_ok = check_docker_available()
    image_cobol_ok = check_docker_image_cached(PARITY_GNUCOBOL_IMAGE) if docker_ok else False
    image_java_ok = check_docker_image_cached(PARITY_JDK_IMAGE) if docker_ok else False

    if PARITY_RUNTIME == "docker" or PARITY_JAVA_RUNTIME == "docker":
        if not docker_ok or not image_cobol_ok or not image_java_ok:
            if PARITY_ALLOW_SKIP:
                return ParityComparison(status="SKIP", skip_reason="Docker or required parity images not available on host.")
            else:
                mismatch = ParityMismatch(
                    target="setup",
                    explanation=f"CI Failure: Docker parity images not found. Docker status: {docker_ok}, COBOL image cached: {image_cobol_ok}, JDK image cached: {image_java_ok}"
                )
                return ParityComparison(status="FAIL", mismatches=[mismatch])

    temp_root = tempfile.mkdtemp(prefix=f"parity_{fixture.name}_")
    cobol_run_dir = os.path.join(temp_root, "cobol-run")
    java_run_dir = os.path.join(temp_root, "java-run")
    
    os.makedirs(cobol_run_dir, exist_ok=True)
    os.makedirs(java_run_dir, exist_ok=True)

    # Copy identical inputs to each isolated directory
    if fixture.input_files:
        for k, v in fixture.input_files.items():
            for d in (cobol_run_dir, java_run_dir):
                p = os.path.join(d, k)
                os.makedirs(os.path.dirname(p), exist_ok=True)
                with open(p, "wb") as f:
                    f.write(v)

    # 2. Run GnuCOBOL baseline
    cobol_res = run_cobol_baseline(fixture, cobol_run_dir)
    if cobol_res.termination_status == "error":
        shutil.rmtree(temp_root, ignore_errors=True)
        mismatch = ParityMismatch(target="cobol_compilation", explanation=cobol_res.error_message)
        return ParityComparison(status="FAIL", mismatches=[mismatch])

    # 3. Run generated Java class
    java_res = run_java_transpiled(fixture, java_run_dir)
    if java_res.termination_status == "error":
        # Keep compile diagnostics
        if PARITY_KEEP_ARTIFACTS_ON_FAILURE:
            fail_dir = os.path.join(PARITY_ARTIFACT_DIR, fixture.name)
            shutil.rmtree(fail_dir, ignore_errors=True)
            shutil.copytree(temp_root, fail_dir, dirs_exist_ok=True)
        shutil.rmtree(temp_root, ignore_errors=True)
        mismatch = ParityMismatch(target="java_compilation", explanation=java_res.error_message)
        return ParityComparison(status="FAIL", mismatches=[mismatch])

    # 4. Compare exit status, stdout, stderr, and declared outputs
    mismatches = []
    
    # Exit code
    if cobol_res.rc != java_res.rc:
        mismatches.append(ParityMismatch(
            target="exit_code",
            explanation=f"COBOL exit code: {cobol_res.rc}, Java exit code: {java_res.rc}"
        ))

    # Stdout comparison (raw bytes)
    m_stdout = compare_raw_bytes("stdout", cobol_res.stdout, java_res.stdout)
    if m_stdout:
        mismatches.append(m_stdout)
        
    # Stderr comparison (raw bytes)
    m_stderr = compare_raw_bytes("stderr", cobol_res.stderr, java_res.stderr)
    if m_stderr:
        mismatches.append(m_stderr)

    # Output files comparison
    for f_name in fixture.declared_outputs:
        c_bytes = cobol_res.files.get(f_name, b"")
        j_bytes = java_res.files.get(f_name, b"")
        m_file = compare_raw_bytes(f"file:{f_name}", c_bytes, j_bytes)
        if m_file:
            mismatches.append(m_file)

    # 5. Clean up or retain temporary directories
    if mismatches:
        if PARITY_KEEP_ARTIFACTS_ON_FAILURE:
            fail_dir = os.path.join(PARITY_ARTIFACT_DIR, fixture.name)
            shutil.rmtree(fail_dir, ignore_errors=True)
            shutil.copytree(temp_root, fail_dir, dirs_exist_ok=True)
        shutil.rmtree(temp_root, ignore_errors=True)
        return ParityComparison(status="FAIL", mismatches=mismatches)

    shutil.rmtree(temp_root, ignore_errors=True)
    return ParityComparison(status="PASS")
