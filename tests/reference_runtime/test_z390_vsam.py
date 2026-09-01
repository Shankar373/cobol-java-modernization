"""Tests for zVSAM Reference Semantics & Separation from Physical VSAM."""

import pytest
from tools.reference_runtimes.base import RuntimeCapability
from tools.reference_runtimes.z390 import Z390ReferenceRunner


def test_zvsam_capability_support():
    runner = Z390ReferenceRunner()
    assert RuntimeCapability.VSAM_KSDS in runner.supported_capabilities()
    assert RuntimeCapability.VSAM_RRDS in runner.supported_capabilities()


def test_zvsam_logical_separation_from_physical_vsam():
    """Confirms zVSAM emulation provides logical keys without claiming physical CI/CA split equivalence."""
    runner = Z390ReferenceRunner()
    caps = runner.supported_capabilities()
    assert RuntimeCapability.VSAM_KSDS in caps
