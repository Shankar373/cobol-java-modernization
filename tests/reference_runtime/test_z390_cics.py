"""Tests for zCICS Reference Semantics."""

import pytest
from tools.reference_runtimes.base import RuntimeCapability
from tools.reference_runtimes.z390 import Z390ReferenceRunner


def test_zcics_capability_support():
    runner = Z390ReferenceRunner()
    assert RuntimeCapability.CICS_REST in runner.supported_capabilities()
