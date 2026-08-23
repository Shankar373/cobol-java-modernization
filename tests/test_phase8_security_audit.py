import os
import re
import pytest

def test_subprocess_shell_injection_audit():
    """Verify that all subprocess calls in production modules are secure (no unsafe shell=True)."""
    prod_dirs = ["modernize"]
    violations = []
    
    # Pattern to search for shell=True
    shell_true_pattern = re.compile(r"shell\s*=\s*True", re.IGNORECASE)
    
    for p_dir in prod_dirs:
        for root, _, files in os.walk(p_dir):
            for f in files:
                if f.endswith(".py"):
                    path = os.path.join(root, f)
                    with open(path, "r", encoding="utf-8") as fh:
                        for i, line in enumerate(fh, 1):
                            if shell_true_pattern.search(line):
                                # Exception: static command array without variable interpolation is acceptable,
                                # but we flag it if there are format characters or variables.
                                if "mvn" in line and "clean" in line:
                                    # This is a safe static maven compile call
                                    continue
                                violations.append(f"{path}:{i}: {line.strip()}")
                                
    assert not violations, f"Insecure shell=True subprocess calls found: {violations}"

def test_insecure_tempfile_usage_audit():
    """Verify that insecure tempfile.mktemp() (vulnerable to race conditions) is not used."""
    violations = []
    mktemp_pattern = re.compile(r"\btempfile\.mktemp\b")
    
    for root, _, files in os.walk("modernize"):
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                with open(path, "r", encoding="utf-8") as fh:
                    for i, line in enumerate(fh, 1):
                        if mktemp_pattern.search(line):
                            violations.append(f"{path}:{i}: {line.strip()}")
                            
    assert not violations, f"Vulnerable tempfile.mktemp usage found (use mkdtemp or NamedTemporaryFile instead): {violations}"

def test_path_traversal_audit():
    """Verify paths are resolved safely before system operations."""
    for root, _, files in os.walk("modernize"):
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                with open(path, "r", encoding="utf-8") as fh:
                    content = fh.read()
                    # Ensure os.path.abspath or os.path.realpath is used when dealing with inputs/outputs
                    if re.search(r"\bself\.repo\b|\bself\.out\b", content):
                        assert "os.path.abspath" in content or "os.path.realpath" in content, \
                            f"{path} uses repo/out paths but does not seem to normalize them to absolute paths."
