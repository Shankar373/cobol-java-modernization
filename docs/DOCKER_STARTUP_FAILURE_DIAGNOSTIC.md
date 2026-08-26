# Docker Startup Failure Diagnostic

## 1. Executive Summary
The Dockerized version of the COBOL → Native Java/Spring modernization platform fails to start, crash-looping with a Python `SyntaxError`. While the application runs successfully when executed directly on the Windows host using Python 3.14, the Docker container uses Python 3.10, which is incompatible with the codebase's syntax. Additionally, we identified a critical architectural gap where the containerized orchestrator cannot access the Docker daemon, meaning the pipeline will fail at the compilation stages even if the syntax errors are patched.

---

## 2. Exact Failure
The container logs report a syntax error when `ui.py` attempts to import the pipeline orchestrator:

```text
Traceback (most recent call last):
  File "/app/ui.py", line 33, in <module>
    import cobol_migrate as engine
  File "/app/cobol_migrate.py", line 921
    n.append(f"                       DISPLAY {' ' + ' \"|\" '.join(emits)}")
                                                                            ^
SyntaxError: f-string expression part cannot include a backslash
```

---

## 3. Root Cause

### 3.1 Incompatible Python Runtime inside the Image
The `Dockerfile` is built on top of `eclipse-temurin:17-jdk-jammy`, which runs Ubuntu Jammy (22.04). Installing the default `python3` package via `apt` pulls **Python 3.10.12**. 

### 3.2 Code Syntax Incompatibility (PEP 701)
The codebase uses backslashes inside f-string expressions (e.g. `\' "|\" \'.join(...)`). 
*   **PEP 701** (introduced in Python 3.12) relaxed f-string restrictions, allowing backslashes in expression parts.
*   In Python versions prior to 3.12 (such as Python 3.10 inside the container), this syntax causes an immediate `SyntaxError` at parse time.

### 3.3 Secondary Syntax Error (Unchecked Crash)
We discovered a secondary syntax error inside `modernize/native_generator.py:1695`:
```python
src_expr = f"\"{source[1:-1].replace('\"', '\\\"')}\""
```
This expression also contains backslashes inside curly braces. Patching the first error in `cobol_migrate.py` would cause the container to fail on this secondary syntax error during modernization runs.

---

## 4. Evidence

### Host Environment Status (Python 3.14.3)
All files compile successfully on the host:
```powershell
PS C:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test> python --version
Python 3.14.3
PS C:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test> python -m py_compile cobol_migrate.py ui.py
PS C:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test> echo $LASTEXITCODE
0
```

### Docker Container Status (Python 3.10.12)
Running compilation checks inside the container reproduces the syntax errors:
```powershell
PS C:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test> docker run --rm cobol-modernizer:latest python --version
Python 3.10.12

PS C:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test> docker run --rm cobol-modernizer:latest python -m py_compile /app/cobol_migrate.py
  File "/app/cobol_migrate.py", line 921
    n.append(f"                       DISPLAY {' ' + ' \"|\" '.join(emits)}")
                                                                            ^
SyntaxError: f-string expression part cannot include a backslash

PS C:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test> docker run --rm cobol-modernizer:latest python -m compileall /app/modernize
Listing '/app/modernize'...
Compiling '/app/modernize/native_generator.py'...
***   File "/app/modernize/native_generator.py", line 1695
    src_expr = f"\"{source[1:-1].replace('\"', '\\\"')}\""
                                                          ^
SyntaxError: f-string expression part cannot include a backslash
```

---

## 5. Host vs Docker Environment

| Component | Host | Docker | Expected | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Python Version** | 3.14.3 | 3.10.12 | `>= 3.12` | `MISCONFIGURED` |
| **Java JDK** | 25.0.3 | 17.0.20 | `>= 17` | `READY` |
| **Maven** | 3.9.16 | 3.6.3 | `>= 3.9` | `READY` (inside build) |
| **Docker CLI** | Yes | No | Yes (for sub-containers) | `MISSING` |
| **Docker Socket** | Yes (Daemon Active) | No (Socket not mounted) | Yes | `MISSING` |
| **Workspace Dir** | Accessible | Mounted to `/app/workspace` | Accessible | `READY` |

---

## 6. Docker Build Analysis
Running `docker compose build --no-cache` completes successfully. This indicates that **successful Docker builds do NOT prove runtime readiness**:
*   The `Dockerfile` contains no compile check stages for Python files.
*   Because Python is an interpreted language, the syntax errors are not triggered until execution time (`ui.py` startup).

---

## 7. Volume / Mount Analysis
The volumes defined in `docker-compose.yml` (`workspace` and `maven-cache`) are correctly mounted and do not overwrite or shadow the source code in `/app`. However:
*   The Docker socket `/var/run/docker.sock` is **not** mounted.
*   Without this mount, the containerized application cannot spawn the sub-containers required for transpilation/compilation validation stages.

---

## 8. Dependency Analysis
The Python orchestrator relies entirely on the Python Standard Library for its runtime; hence, the lack of `pip install` commands in the `Dockerfile` is expected and not a cause of failure. Java dependencies are successfully pre-cached inside the image using the seed POM files.

---

## 9. Secondary Failures: Docker-out-of-Docker (DooD) Gap
If the Python syntax errors are patched, the containerized application will still fail during execution at **Stage 4 (Baseline)** and **Stage 5 (Transpile)**:
1.  The orchestrator triggers compilation and transpilation stages by executing shells commands:
    *   `docker run --rm -v ... hurriedreformist/gnucobol:3.1-builder ...`
    *   `docker run --rm -v ... opensourcecobol/opensourcecobol4j:2.0.0 ...`
2.  Because the Docker CLI is not installed in the container image and `/var/run/docker.sock` is not mapped, any execution of these commands inside the container will fail with a `FileNotFoundError` (Command 'docker' not found).

---

## 10. Security Findings
*   Variables in `docker-compose.yml` (`DB2_URL`, `DB2_USER`, `DB2_PASSWORD`) are commented out and act as configuration templates.
*   No `.env` file exists in the repository, and no secrets are exposed in logs or files.

---

## 11. Impact on Project
*   **Host Execution**: Fully operational (`READY`). Discovers, transpiles, compiles with Maven, runs H2 verification, and completes all 509 test assertions.
*   **Dockerized Execution**: Non-operational (`BLOCKED`). The container crash-loops at startup.
*   **Real DB2 Verification**: Remains `ENVIRONMENT_BLOCKED` on both host and Docker due to local resource constraints and missing config.

---

## 12. Recommended Fix

### Step 1: Make Code Syntactically Backward-Compatible (Python 3.10+)
Modify the f-string expressions in the source files to resolve string formatting outside the curly braces.

*   **In [`cobol_migrate.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/cobol_migrate.py#L921)**:
    ```python
    # Before:
    n.append(f"                       DISPLAY {' ' + ' \"|\" '.join(emits)}")
    # After:
    emits_str = ' ' + ' "|" '.join(emits)
    n.append(f"                       DISPLAY {emits_str}")
    ```

*   **In [`modernize/native_generator.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/native_generator.py#L1695)**:
    ```python
    # Before:
    src_expr = f"\"{source[1:-1].replace('\"', '\\\"')}\""
    # After:
    escaped_source = source[1:-1].replace('"', '\\"')
    src_expr = f"\"{escaped_source}\""
    ```

### Step 2: Resolve Docker-out-of-Docker Capability
To allow the containerized platform to invoke GnuCOBOL and OpenSourceCOBOL4J compilers:
1.  **Install Docker CLI**: Add Docker CLI installation instructions to the `Dockerfile` runtime build.
2.  **Mount Docker Socket**: Update `docker-compose.yml` to mount the host's Docker socket:
    ```yaml
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    ```

---

## 13. Verification Plan After Fix
1.  Run `docker compose build --no-cache` to build a clean image.
2.  Run `docker compose up -d` and verify that `docker compose ps` shows `cobol-modernizer` as `healthy` / `running`.
3.  Execute E2E API tests via `pytest` or Python requests driving the container's port `8787` and confirm pipeline stages 4 and 5 complete successfully.

---

## 14. Final Classification

```text
CLASSIFICATION = MISCONFIGURED
```

**Justification**: The project functions perfectly when run directly on the host. However, the Docker deployment configuration is misconfigured: it provisions a Python runtime version (3.10) that is incompatible with the codebase's syntax (which requires Python >=3.12 due to backslashes in f-strings) and fails to set up Docker-out-of-Docker socket sharing.
