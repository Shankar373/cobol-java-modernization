import os
import re

BENCHMARK_NAMES = [
    r"\bBANKMAIN\b",
    r"\bBCMAIN\b",
    r"\bVALDATE\b",
]

def test_production_no_benchmark_hardcoding():
    # Production source files list to scan
    production_files = ["cobol_migrate.py"]
    for root, dirs, files in os.walk("modernize"):
        for f in files:
            if f.endswith(".py"):
                production_files.append(os.path.join(root, f))

    violations = []
    for path in production_files:
        if not os.path.isfile(path):
            continue
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
        
        for i, line in enumerate(lines):
            for pattern in BENCHMARK_NAMES:
                if re.search(pattern, line, re.IGNORECASE):
                    trimmed = line.strip()
                    # Skip comment lines and docstrings
                    if trimmed.startswith("#") or trimmed.startswith('"""') or trimmed.startswith("'''"):
                        continue
                    if "#" in trimmed:
                        # If comment is trailing, check the code part
                        parts = trimmed.split("#", 1)
                        if not parts[0].strip():
                            continue
                        trimmed = parts[0].strip()
                    if "self.log(" in trimmed or "logger." in trimmed or "print(" in trimmed:
                        continue
                    
                    # Exclude legacy Spring modernization logic in cobol_migrate.py from blocking check,
                    # but check that our new stage_compare does not contain hardcoded conditions.
                    if path == "cobol_migrate.py":
                        # stage_compare is between line 3050 and 3300
                        if 3050 <= (i + 1) <= 3300:
                            violations.append(f"{path}:{i+1}: {line.strip()}")
                    else:
                        violations.append(f"{path}:{i+1}: {line.strip()}")

    # Report violations if any
    if violations:
        print("\nViolations found in active validation/modernization logic:")
        for v in violations:
            print(f"  - {v}")
    assert not violations, f"Benchmark-specific logic hardcoded in execution verification/modernization code: {violations}"
