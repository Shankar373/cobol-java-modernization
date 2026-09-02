"""Comprehensive boundary and fail-closed tests for CICS TS integration.

In accordance with the Ponytail Constitution:
- In-memory COMMAREA and Spring REST modernization is explicitly SIMULATED.
- Real IBM CICS TS status remains strictly UNPROVEN unless live mainframe connection is proven.
- When unconfigured, RealCicsTsReferenceAdapter fails closed.
"""

import os
import pytest
from tools.reference_runtimes.cics_runtime import (
    CicsResponseCode,
    CicsTransactionContext,
    CicsTsStatus,
    ModernizedCicsRuntime,
    RealCicsTsReferenceAdapter,
)
from tools.reference_runtimes.certification_policy import CertificationPolicy, WorkloadCertificationStatus


def test_cics_context_channel_and_container():
    ctx = CicsTransactionContext(trans_id="TX01")
    ctx.put_container("CHAN1", "CONT1", b"PAYLOAD_DATA_123")
    data = ctx.get_container("CHAN1", "CONT1")
    assert data == b"PAYLOAD_DATA_123"
    assert ctx.get_container("CHAN1", "NONEXISTENT") is None


def test_modernized_cics_runtime_link_and_commarea():
    runtime = ModernizedCicsRuntime()
    
    def target_handler(ctx: CicsTransactionContext):
        return f"PROCESSED_{ctx.commarea}"

    runtime.register_program("PROG2", target_handler)
    
    caller_ctx = CicsTransactionContext(trans_id="TX01", commarea="INPUT_DATA")
    resp, result = runtime.link(caller_ctx, "PROG2", commarea="NEW_DATA")
    assert resp == CicsResponseCode.NORMAL
    assert result == "PROCESSED_NEW_DATA"


def test_modernized_cics_runtime_link_missing_program():
    runtime = ModernizedCicsRuntime()
    caller_ctx = CicsTransactionContext(trans_id="TX01")
    resp, result = runtime.link(caller_ctx, "MISSING_PROG")
    assert resp == CicsResponseCode.PGMIDERR
    assert result is None
    assert caller_ctx.response_code == CicsResponseCode.PGMIDERR


def test_modernized_cics_runtime_xctl():
    runtime = ModernizedCicsRuntime()
    executed = []
    
    def prog_b(ctx: CicsTransactionContext):
        executed.append(ctx.commarea)

    runtime.register_program("PROGB", prog_b)
    caller_ctx = CicsTransactionContext(trans_id="TX01", commarea="START")
    resp = runtime.xctl(caller_ctx, "PROGB", commarea="TRANSFERRED")
    assert resp == CicsResponseCode.NORMAL
    assert executed == ["TRANSFERRED"]


def test_modernized_cics_runtime_syncpoint():
    runtime = ModernizedCicsRuntime()
    ctx = CicsTransactionContext(trans_id="TX01")
    resp_commit = runtime.syncpoint(ctx, rollback=False)
    assert resp_commit == CicsResponseCode.NORMAL
    assert ctx.syncpoints == ["COMMIT"]
    
    resp_rb = runtime.syncpoint(ctx, rollback=True)
    assert resp_rb == CicsResponseCode.NORMAL
    assert ctx.syncpoints == ["COMMIT", "ROLLBACK"]


def test_real_cics_ts_adapter_fails_closed_unconfigured():
    env_backup = {k: os.environ.pop(k, None) for k in ["CICS_TS_HOST", "CICS_TS_APPLID"]}
    try:
        adapter = RealCicsTsReferenceAdapter()
        assert adapter.is_configured is False
        status = adapter.detect_environment()
        assert status == CicsTsStatus.UNAVAILABLE
        assert len(adapter.diagnostics) > 0
        
        # Invocation fails closed
        res = adapter.invoke_transaction("TX01", b"TEST")
        assert res["status"] == CicsTsStatus.UNAVAILABLE.value
        assert res["resp"] == CicsResponseCode.SYSIDERR.value
        assert "not connected" in res["error"]
    finally:
        for k, v in env_backup.items():
            if v is not None:
                os.environ[k] = v


def test_certification_policy_cics_fail_closed():
    manifest = {
        "requires": {"batch": False, "sql": False, "vsam": False, "cics": True, "ebcdic": False, "jcl": False},
        "detected_constructs": ["EXEC CICS LINK", "EXEC CICS RETURN"]
    }
    res = CertificationPolicy.evaluate(
        manifest,
        gate1_passed=True,
        gate2_passed=True,
        real_ibm_cics_tested=False,
    )
    assert res.subsystem_evaluations["cics"] == "SIMULATED"
    assert "Spring REST / in-memory COMMAREA simulation" in res.limitations[0]
    assert res.verdict == WorkloadCertificationStatus.VERIFIED_FOR_DEFINED_SCOPE
