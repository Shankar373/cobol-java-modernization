import json
import os
import shutil
import tempfile
import pytest
from modernize.native_pipeline import NativePipeline

COBOL_H2_STANDALONE = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. H2STAND.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  SQLCA-VARIABLES.
           05  SQLCODE    PIC S9(9) COMP.
           05  SQLSTATE   PIC X(5).
       01  WS-ITEM.
           05  WS-ID      PIC S9(9) COMP VALUE 42.
           05  WS-DESC    PIC X(20) VALUE SPACES.
       PROCEDURE DIVISION.
           EXEC SQL
               SELECT ITEM_DESC
               INTO :WS-DESC
               FROM INVENTORY
               WHERE ITEM_ID = :WS-ID
           END-EXEC.
           DISPLAY "SQLCODE: " SQLCODE
           DISPLAY "ITEM: " WS-DESC
           GOBACK.
"""

SQL_INVENTORY_SEED = """CREATE TABLE IF NOT EXISTS INVENTORY (ITEM_ID INT, ITEM_DESC VARCHAR(50));
INSERT INTO INVENTORY (ITEM_ID, ITEM_DESC) VALUES (42, 'H2-STANDALONE-ITEM');
"""


def _create_h2_standalone_fixture_repo(repo_dir: str):
    """Create a repo fixture with data/*.sql seeds and NO mock_db.yaml."""
    src_dir = os.path.join(repo_dir, "src")
    data_dir = os.path.join(repo_dir, "data")
    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)

    cob_path = os.path.join(src_dir, "H2STAND.cob")
    with open(cob_path, "w", encoding="utf-8") as fh:
        fh.write(COBOL_H2_STANDALONE)

    seed_path = os.path.join(data_dir, "inventory.sql")
    with open(seed_path, "w", encoding="utf-8") as fh:
        fh.write(SQL_INVENTORY_SEED)

    cfg = {
        "main_program": "H2STAND",
        "sources": ["src/H2STAND.cob"]
    }
    with open(os.path.join(repo_dir, "migration_config.json"), "w", encoding="utf-8") as fh:
        json.dump(cfg, fh)


def test_p0_002_h2_standalone_seed_lifecycle():
    """
    P0-002 (=B3) Verification:
    Verify that MockSqlService.initialize() ordering enables H2 standalone DDL and seed queries.

    In the defective state, MockSqlService.initialize() was emitted in main() before execute().
    Because MockSqlService.initialize() pre-sets SpringContextHelper.jdbcTemplate, the DDL
    and seed block in execute() (`if (jdbcTemplate == null)`) was skipped, leading to unseeded
    tables and silent SQLCODE -1 / empty results for repos with data/*.sql.

    With the fix:
    - MockSqlService.initialize() is emitted AFTER the DDL/seed block in execute().
    - Standalone H2 runs execute CREATE TABLE and INSERT seeds, returning real data.
    """
    temp_repo = tempfile.mkdtemp()
    temp_out = tempfile.mkdtemp()

    try:
        _create_h2_standalone_fixture_repo(temp_repo)

        # Expected stdout has signed SQLCODE +000000000 and the seeded inventory item
        expected_stdout = "SQLCODE: +000000000\nITEM: H2-STANDALONE-ITEM  \n"
        baseline_dir = os.path.join(temp_out, "baseline", "legacy")
        os.makedirs(baseline_dir, exist_ok=True)
        with open(os.path.join(baseline_dir, "stdout.txt"), "w", encoding="utf-8") as fh:
            fh.write(expected_stdout)

        # Clear PG environment to enforce standalone H2 execution
        for k in ["PGHOST", "PGPORT", "PGUSER", "PGPASSWORD", "PGDATABASE"]:
            os.environ.pop(k, None)

        pipeline = NativePipeline(temp_repo, temp_out)
        verdict = pipeline.run()

        # 1. Verify pipeline succeeds in standalone H2 mode
        assert verdict == "NATIVE_JAVA_VERIFIED", f"Standalone H2 pipeline failed with verdict: {verdict}"

        # 2. Inspect generated Java source: verify emission location of MockSqlService.initialize()
        java_src_path = os.path.join(pipeline.src_dir, "H2stand.java")
        assert os.path.exists(java_src_path), f"Generated Java file not found at: {java_src_path}"
        with open(java_src_path, "r", encoding="utf-8") as fh:
            java_src = fh.read()

        # Must NOT be in main() before new H2stand().execute();
        main_idx = java_src.find("public static void main(String[] args)")
        assert main_idx != -1, "main() method not found in generated class"
        main_body = java_src[main_idx:]
        assert "MockSqlService.initialize();" not in main_body, (
            "REGRESSION: MockSqlService.initialize() must not be called in main() before execute()"
        )

        # Must be in execute() AFTER the DDL/seed creation block
        execute_idx = java_src.find("public void execute()")
        assert execute_idx != -1, "execute() method not found in generated class"
        execute_body = java_src[execute_idx:main_idx]

        ddl_pos = execute_body.find("CREATE TABLE IF NOT EXISTS")
        mock_init_pos = execute_body.find("MockSqlService.initialize();")
        assert ddl_pos != -1, "DDL generation block missing from execute()"
        assert mock_init_pos != -1, "MockSqlService.initialize() missing from execute()"
        assert mock_init_pos > ddl_pos, (
            "ORDERING DEFECT: MockSqlService.initialize() must be called AFTER DDL/seed setup in execute()"
        )

        # 3. Verify execution observation confirms successful execution with exit code 0
        obs_file = os.path.join(temp_out, "generated", "native_execution_observation.json")
        assert os.path.exists(obs_file)
        with open(obs_file, "r", encoding="utf-8") as fh:
            obs = json.load(fh)
            assert obs["exit_code"] == 0

        # 4. Verify stdout captured the seeded customer record from data/inventory.sql
        stdout_path = os.path.join(temp_out, "results", "native", "stdout.txt")
        assert os.path.exists(stdout_path)
        with open(stdout_path, "r", encoding="utf-8") as fh:
            stdout_content = fh.read()
            assert "H2-STANDALONE-ITEM" in stdout_content
            assert "+000000000" in stdout_content

    finally:
        shutil.rmtree(temp_repo, ignore_errors=True)
        shutil.rmtree(temp_out, ignore_errors=True)


def test_p0_002_h2_standalone_negative_mutation_proof():
    """
    Negative / Mutation proof for P0-002:
    Simulate the pre-remediation defect where MockSqlService.initialize() is called in main()
    before execute(). Verify that the mutated order causes the standalone run to fail or
    diverge because the DDL and seed queries in execute() are skipped.
    """
    temp_repo = tempfile.mkdtemp()
    temp_out = tempfile.mkdtemp()

    try:
        _create_h2_standalone_fixture_repo(temp_repo)

        # Clear PG environment
        for k in ["PGHOST", "PGPORT", "PGUSER", "PGPASSWORD", "PGDATABASE"]:
            os.environ.pop(k, None)

        pipeline = NativePipeline(temp_repo, temp_out)
        # Run stages up to generation
        pipeline.stage_discover()
        pipeline.stage_parse()
        selected_src = pipeline.stage_select_slice()
        pipeline.stage_generate(selected_src)

        java_src_path = os.path.join(pipeline.src_dir, "H2stand.java")
        assert os.path.exists(java_src_path)
        with open(java_src_path, "r", encoding="utf-8") as fh:
            java_src = fh.read()

        # Mutate: remove MockSqlService.initialize() from execute() and place in main() before execute()
        assert "com.systema.modernized.MockSqlService.initialize();" in java_src
        mutated_src = java_src.replace(
            "com.systema.modernized.MockSqlService.initialize();",
            "// MUTANT: removed from execute()"
        )
        mutated_src = mutated_src.replace(
            "new H2stand().execute();",
            "com.systema.modernized.MockSqlService.initialize();\n        new H2stand().execute();"
        )
        with open(java_src_path, "w", encoding="utf-8") as fh:
            fh.write(mutated_src)

        # Build and execute mutant
        build_pass = pipeline.stage_build_gate()
        assert build_pass, "Mutant should compile successfully"
        exec_pass = pipeline.stage_execute_gate(selected_src)

        # In the mutated order, DDL and seed queries were skipped because jdbcTemplate was pre-set in main().
        # Therefore, INVENTORY table does NOT exist in H2.
        # It must NOT return "H2-STANDALONE-ITEM", proving the test distinguishes correct from defective behavior.
        stdout_path = os.path.join(temp_out, "results", "native", "stdout.txt")
        mutant_stdout = ""
        if os.path.exists(stdout_path):
            with open(stdout_path, "r", encoding="utf-8") as fh:
                mutant_stdout = fh.read()

        assert "H2-STANDALONE-ITEM" not in mutant_stdout, (
            f"Mutant unexpectedly retrieved seeded inventory despite skipped DDL/seeds: {mutant_stdout}"
        )
        # Verify that an error or empty result occurred in the mutant
        assert "+000000000" not in mutant_stdout, (
            f"Mutant unexpectedly succeeded with SQLCODE 0: {mutant_stdout}"
        )

    finally:
        shutil.rmtree(temp_repo, ignore_errors=True)
        shutil.rmtree(temp_out, ignore_errors=True)
