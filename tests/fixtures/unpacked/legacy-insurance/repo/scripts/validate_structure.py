from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
required = [
    "README.md", "db2/schema.sql", "db2/seed.sql",
    "cobol/online/CLAIM02.cbl", "cobol/copybooks/CLAIM.cpy",
    "jcl/JOB002_CLAIM_BATCH.jcl", "bms/CLAIMMP.bms", "vsam/policy.ksds",
    "tests/test_golden_reference.py",
]
missing = [p for p in required if not (ROOT/p).exists()]
if missing:
    raise SystemExit("Missing required files: " + ", ".join(missing))
print("STRUCTURE_VALID")
