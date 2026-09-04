"""Tests for z390 Reference Runtime Availability & Graceful Fallback."""

import os
import pytest
from tools.reference_runtimes.base import RuntimeCapability, RuntimeStatus
from tools.reference_runtimes.z390 import Z390ReferenceRunner


def test_z390_runner_instantiation():
    runner = Z390ReferenceRunner(z390_home="/nonexistent/z390")
    assert runner.name == "z390"
    assert RuntimeCapability.BATCH_COBOL in runner.supported_capabilities()
    assert RuntimeCapability.VSAM_KSDS in runner.supported_capabilities()
    assert RuntimeCapability.EBCDIC_NATIVE in runner.supported_capabilities()


def test_z390_unavailable_returns_explicit_status(tmp_path):
    runner = Z390ReferenceRunner(z390_home="/nonexistent/z390", docker_image="nonexistent_z390_image:latest")
    is_avail = runner.is_available()
    valid, msg = runner.validate_environment()
    if not is_avail:
        assert not valid
        res = runner.execute(
            source_files={"TEST.cob": "IDENTIFICATION DIVISION. PROGRAM-ID. TEST."},
            copybooks={},
            input_files={},
            entry_program="TEST",
            work_dir=str(tmp_path),
        )
        assert res.status == RuntimeStatus.UNAVAILABLE
        err = (res.error_message or "").lower()
        assert "not available" in err or "unavailable" in err
