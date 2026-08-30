import os
import shutil
import tempfile
import subprocess
import pytest
from modernize.native_pipeline import NativePipeline

def test_ksds_baseline_differential():
    """Phase 1: Real GnuCOBOL KSDS baseline vs modernized Spring Boot + PostgreSQL.
    Verifies execution parity of WRITE, READ, START, READ NEXT, REWRITE, and DELETE."""
    # Seed/Cleanup Postgres DB table for VSAM KSDS emulation
    cleanup_cmd = [
        "docker", "exec", "-i", "modernization-platform-db-1",
        "psql", "-U", "modernize", "-d", "modernization_db",
        "-c", "DROP TABLE IF EXISTS customer_vsam;"
    ]
    subprocess.run(cleanup_cmd, check=True)

    repo_dir = r"c:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test\tests\repos\ksds_baseline_01"
    tmp_out = tempfile.mkdtemp(prefix="ksds_baseline_")

    try:
        # Set PG connection parameters in environment for host Java run
        os.environ["PGHOST"] = "localhost"
        os.environ["PGPORT"] = "5432"
        os.environ["PGUSER"] = "modernize"
        os.environ["PGPASSWORD"] = "modernize"
        os.environ["PGDATABASE"] = "modernization_db"

        pipe = NativePipeline(repo_dir, tmp_out)
        verdict = pipe.run()

        # Print debug outputs if it fails
        if verdict != "NATIVE_JAVA_VERIFIED":
            print("Verdict:", verdict)
            obs_path = os.path.join(tmp_out, "generated", "native_execution_observation.json")
            if os.path.exists(obs_path):
                with open(obs_path, "r", encoding="utf-8") as f:
                    print("Observation:", f.read())

            # Print legacy stdout
            legacy_stdout_path = os.path.join(tmp_out, "baseline", "legacy", "stdout.txt")
            if os.path.exists(legacy_stdout_path):
                with open(legacy_stdout_path, "r", encoding="utf-8") as f:
                    print("Legacy Stdout:\n", f.read())

            # Print modernized stdout
            modernized_stdout_path = os.path.join(tmp_out, "results", "native", "stdout.txt")
            if os.path.exists(modernized_stdout_path):
                with open(modernized_stdout_path, "r", encoding="utf-8") as f:
                    print("Modernized Stdout:\n", f.read())

        assert verdict == "NATIVE_JAVA_VERIFIED"
    finally:
        shutil.rmtree(tmp_out, ignore_errors=True)
