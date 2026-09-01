"""Tests for z390 Batch Execution & Mock Fallback Semantics."""

import pytest
from tools.reference_runtimes.base import RuntimeCapability, RuntimeStatus
from tools.reference_runtimes.z390 import Z390ReferenceRunner


def test_z390_batch_capabilities():
    runner = Z390ReferenceRunner()
    caps = runner.supported_capabilities()
    assert RuntimeCapability.BATCH_COBOL in caps
    assert RuntimeCapability.EBCDIC_NATIVE in caps


def test_z390_batch_execution_isolation(tmp_path):
    runner = Z390ReferenceRunner(z390_home="/dummy/path")
    res = runner.execute(
        source_files={"BATCH01.cob": "       IDENTIFICATION DIVISION.\n       PROGRAM-ID. BATCH01.\n       PROCEDURE DIVISION.\n           STOP RUN.\n"},
        copybooks={},
        input_files={},
        entry_program="BATCH01",
        work_dir=str(tmp_path),
    )
    assert res.runtime_name == "z390"
    if not runner.is_available():
        assert res.status == RuntimeStatus.UNAVAILABLE
