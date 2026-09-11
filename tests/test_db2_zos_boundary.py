"""Comprehensive boundary and fail-closed tests for IBM DB2 z/OS integration.

In accordance with the Ponytail Constitution:
- Local/Docker relational database testing does NOT prove live IBM DB2 z/OS.
- When unconfigured or offline, RealDb2ZosAdapter must fail closed (UNAVAILABLE).
- SQLCODE mapping accurately reflects DB2 z/OS return codes.
- Certification classification for REAL_DB2_ZOS remains strictly UNPROVEN.
"""

import os
import pytest
from tools.reference_runtimes.database import (
    DatabaseReferenceRuntime,
    DatabaseValidationMode,
    Db2SqlCodeMapper,
    Db2ZosConnectionConfig,
    Db2ZosStatus,
    RealDb2ZosAdapter,
)
from tools.reference_runtimes.certification_policy import CertificationPolicy, WorkloadCertificationStatus


def test_sqlcode_mapper_success():
    res = Db2SqlCodeMapper.map_sqlcode(0)
    assert res["status"] == "SUCCESS"
    assert res["ansi_sqlstate"] == "00000"


def test_sqlcode_mapper_not_found():
    res = Db2SqlCodeMapper.map_sqlcode(100)
    assert res["status"] == "NOT_FOUND"
    assert res["ansi_sqlstate"] == "02000"


def test_sqlcode_mapper_duplicate_key():
    res = Db2SqlCodeMapper.map_sqlcode(-803)
    assert res["status"] == "DUPLICATE_KEY"
    assert res["ansi_sqlstate"] == "23505"


def test_sqlcode_mapper_resource_unavailable():
    res = Db2SqlCodeMapper.map_sqlcode(-904)
    assert res["status"] == "RESOURCE_UNAVAILABLE"
    assert res["ansi_sqlstate"] == "57011"


def test_sqlcode_mapper_deadlock_rollback():
    res = Db2SqlCodeMapper.map_sqlcode(-911)
    assert res["status"] == "DEADLOCK_TIMEOUT"
    assert res["ansi_sqlstate"] == "40001"


def test_sqlcode_mapper_null_indicator():
    res = Db2SqlCodeMapper.map_sqlcode(-305)
    assert res["status"] == "NULL_INDICATOR_MISSING"
    assert res["ansi_sqlstate"] == "22002"


def test_db2_zos_config_unconfigured_by_default():
    # Ensure environment variables do not create false configuration
    env_backup = {k: os.environ.pop(k, None) for k in ["DB2_ZOS_HOST", "DB2_ZOS_LOCATION", "DB2_ZOS_USER"]}
    try:
        config = Db2ZosConnectionConfig()
        assert config.is_configured is False
    finally:
        for k, v in env_backup.items():
            if v is not None:
                os.environ[k] = v


def test_real_db2_zos_adapter_fails_closed_when_unconfigured():
    env_backup = {k: os.environ.pop(k, None) for k in ["DB2_ZOS_HOST", "DB2_ZOS_LOCATION", "DB2_ZOS_USER"]}
    try:
        adapter = RealDb2ZosAdapter()
        status = adapter.detect_environment()
        assert status == Db2ZosStatus.UNAVAILABLE
        assert len(adapter.diagnostics) > 0
        
        # Execution must fail closed
        exec_res = adapter.execute_sql("SELECT 1 FROM SYSIBM.SYSDUMMY1")
        assert exec_res["status"] == Db2ZosStatus.UNAVAILABLE.value
        assert exec_res["sqlcode"] == Db2SqlCodeMapper.SQLCODE_RESOURCE_UNAVAILABLE
    finally:
        for k, v in env_backup.items():
            if v is not None:
                os.environ[k] = v


def test_real_db2_zos_classification_remains_unproven():
    runtime_local = DatabaseReferenceRuntime(DatabaseValidationMode.LOCAL_RELATIONAL)
    assert runtime_local.certification_classification == "PROVEN_FOR_TESTED_SCOPE"
    
    runtime_docker = DatabaseReferenceRuntime(DatabaseValidationMode.DOCKER_RELATIONAL)
    assert runtime_docker.certification_classification == "PROVEN_FOR_TESTED_SCOPE"
    
    runtime_zos = DatabaseReferenceRuntime(DatabaseValidationMode.REAL_DB2_ZOS)
    assert runtime_zos.certification_classification == "UNPROVEN"


def test_certification_policy_db2_fail_closed():
    manifest = {
        "requires": {"batch": True, "sql": True, "vsam": False, "cics": False, "ebcdic": False, "jcl": False},
        "detected_constructs": ["EXEC SQL SELECT"]
    }
    # When real_ibm_db2_zos_tested is False, status must be PROVEN_FOR_TESTED_SCOPE (local) and limitations noted
    res = CertificationPolicy.evaluate(
        manifest,
        gate1_passed=True,
        gate2_passed=True,
        real_ibm_db2_zos_tested=False,
    )
    assert res.subsystem_evaluations["db2"] == "PROVEN_FOR_TESTED_SCOPE"
    assert "live IBM DB2 z/OS connection is UNPROVEN" in res.limitations[0]
    assert res.verdict == WorkloadCertificationStatus.VERIFIED_FOR_DEFINED_SCOPE
