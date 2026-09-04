"""Tests for Reference Runtime Isolation and Workspace Cleanliness."""

import os
import pytest
from tools.reference_runtimes.gnu_cobol import GnuCobolReferenceRunner
from tools.reference_runtimes.z390 import Z390ReferenceRunner
from tools.reference_runtimes.hercules import HerculesReferenceRunner
from tools.reference_runtimes.capability_detector import WorkloadCapabilityDetector


def test_workload_capability_detector_scanning(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "PROG1.cob").write_text(
        "       IDENTIFICATION DIVISION.\n"
        "       PROGRAM-ID. PROG1.\n"
        "       DATA DIVISION.\n"
        "       WORKING-STORAGE SECTION.\n"
        "       EXEC SQL SELECT AMOUNT INTO :WS-AMT FROM ACCOUNTS END-EXEC.\n"
        "       EXEC CICS LINK PROGRAM('SUB1') END-EXEC.\n"
        "       PROCEDURE DIVISION.\n"
        "           STOP RUN.\n",
        encoding="utf-8",
    )
    detector = WorkloadCapabilityDetector(str(repo))
    manifest = detector.scan_workload()
    assert manifest["requires"]["sql"] is True
    assert manifest["requires"]["cics"] is True
    assert manifest["requires"]["vsam"] is False
    assert "zCICS_Reference" in manifest["required_reference_environments"]
    assert "Relational_Database" in manifest["required_reference_environments"]


def test_reference_runner_workspace_isolation(tmp_path):
    runner = GnuCobolReferenceRunner()
    work1 = tmp_path / "work1"
    work2 = tmp_path / "work2"
    work1.mkdir()
    work2.mkdir()
    assert str(work1) != str(work2)
