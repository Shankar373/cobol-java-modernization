"""Adversarial verification and fail-closed security tests.

Covers Phase 32 adversarial test matrix:
- ADV-01: Self-comparison detection in Gate 1
- ADV-02: Self-comparison detection in Gate 2
- ADV-03: Missing required input file rejection
- ADV-04: Non-empty baseline vs zero-byte output rejection
- ADV-05: Sentinel log spoofing with process failure rejection
"""

import os
import shutil
import tempfile
import pytest
from cobol_migrate import Pipeline

@pytest.fixture
def temp_workspace():
    td = tempfile.mkdtemp(prefix="adv_test_")
    repo = os.path.join(td, "repo")
    out = os.path.join(td, "out")
    os.makedirs(os.path.join(repo, "src"), exist_ok=True)
    os.makedirs(os.path.join(repo, "data", "in"), exist_ok=True)
    yield repo, out
    shutil.rmtree(td, ignore_errors=True)

def test_adv_01_self_comparison_rejection_gate1(temp_workspace):
    """ADV-01: Gate 1 rejects self-comparison when baseline and results point to same directory."""
    repo, out = temp_workspace
    p = Pipeline(repo, out)
    baseline_dir = os.path.join(out, "baseline", "legacy")
    os.makedirs(baseline_dir, exist_ok=True)
    results_dir = os.path.join(out, "results", "java")
    if os.path.exists(results_dir):
        shutil.rmtree(results_dir)
    # Simulate malicious or mistaken symlink / junction / identical directory pointing to baseline
    # On Windows, we can test realpath equality by having both point to baseline_dir directly
    p.set_data("discover", {"entry": "TEST", "output_dirs": []})
    
    # Run stage_compare with both pointing to baseline_dir
    # We patch results_dir to equal baseline_dir
    original_stage_compare = p.stage_compare
    # Test through Pipeline stage execution
    p.set_data("execution_scenario", {"scenario_id": "non_interactive_default"})
    p.set_data("legacy", {"run_rc": 0})
    p.set_data("execute", {"rc": 0})
    
    # Create identical directories
    os.makedirs(os.path.join(out, "baseline", "legacy"), exist_ok=True)
    with open(os.path.join(out, "baseline", "legacy", "out.txt"), "w") as f:
        f.write("SAMPLE_DATA\n")
    os.makedirs(os.path.join(out, "results", "java"), exist_ok=True)
    with open(os.path.join(out, "results", "java", "out.txt"), "w") as f:
        f.write("SAMPLE_DATA\n")
        
    # Now simulate identical path
    import unittest.mock as mock
    with mock.patch("os.path.realpath", side_effect=lambda p: "C:/identical/path" if "baseline" in p or "results" in p else p):
        success, msg, _ = p.stage_compare()
        assert not success
        assert "Self-comparison vulnerability detected" in msg

def test_adv_02_self_comparison_rejection_gate2(temp_workspace):
    """ADV-02: Gate 2 rejects self-comparison when baseline and modernized directory resolve identically."""
    repo, out = temp_workspace
    p = Pipeline(repo, out)
    p.set_data("discover", {"entry": "TEST", "copybook_dirs": [], "file_ops": {}})
    p.set_data("baseline_files", ["data/out/report.txt"])
    
    mod_dir = os.path.join(out, "modernized")
    os.makedirs(os.path.join(mod_dir, "target"), exist_ok=True)
    jar_file = os.path.join(mod_dir, "target", "modernized-1.0.0.jar")
    with open(jar_file, "w") as f:
        f.write("dummy-jar")
        
    import unittest.mock as mock
    with mock.patch("shutil.which", return_value="fake_bin"), \
         mock.patch("cobol_migrate.sh", return_value=mock.Mock(returncode=0)), \
         mock.patch("subprocess.Popen") as mock_popen, \
         mock.patch("os.path.realpath", side_effect=lambda p: "C:/same/dir" if "baseline" in p or "modernized" in p else p):
        
        proc_mock = mock.Mock()
        proc_mock.poll.return_value = 0
        proc_mock.returncode = 0
        mock_popen.return_value = proc_mock
        
        success, msg, _ = p.stage_validate()
        assert not success
        assert "Self-comparison vulnerability detected" in msg

def test_adv_03_missing_required_input_fails_closed(temp_workspace):
    """ADV-03: Gate 2 fails closed if an explicit input ASSIGN is missing/unresolvable."""
    repo, out = temp_workspace
    p = Pipeline(repo, out)
    p.set_data("discover", {
        "entry": "TEST",
        "copybook_dirs": [],
        "file_ops": {"TEST.cob": {"IN-FILE": {"is_input": True}}},
        "file_assigns": {"TEST.cob": [{"logical_name": "IN-FILE", "assign_path": "data/in/nonexistent.dat"}]}
    })
    mod_dir = os.path.join(out, "modernized")
    os.makedirs(os.path.join(mod_dir, "target"), exist_ok=True)
    jar_file = os.path.join(mod_dir, "target", "modernized-1.0.0.jar")
    with open(jar_file, "w") as f:
        f.write("dummy-jar")
        
    import unittest.mock as mock
    with mock.patch("shutil.which", return_value="fake_bin"), \
         mock.patch("cobol_migrate.sh", return_value=mock.Mock(returncode=0)):
        success, msg, _ = p.stage_validate()
        assert not success
        assert "Required batch input file missing or unresolvable" in msg

def test_adv_04_zero_byte_mismatch_detection(temp_workspace):
    """ADV-04: Non-empty baseline vs empty/zero-byte output in Gate 1 fails comparison."""
    repo, out = temp_workspace
    p = Pipeline(repo, out)
    p.set_data("discover", {"entry": "TEST", "output_dirs": ["data/out"]})
    p.set_data("execution_scenario", {"scenario_id": "non_interactive_default"})
    p.set_data("legacy", {"run_rc": 0})
    p.set_data("execute", {"rc": 0})
    
    baseline_dir = os.path.join(out, "baseline", "legacy")
    results_dir = os.path.join(out, "results", "java")
    os.makedirs(os.path.join(baseline_dir, "data", "out"), exist_ok=True)
    os.makedirs(os.path.join(results_dir, "data", "out"), exist_ok=True)
    
    # Baseline has 100 bytes, Java produced 0 bytes
    with open(os.path.join(baseline_dir, "data", "out", "report.txt"), "w") as f:
        f.write("A" * 100 + "\n")
    with open(os.path.join(results_dir, "data", "out", "report.txt"), "w") as f:
        f.write("")
        
    success, msg, _ = p.stage_compare()
    assert not success
    assert p.data("compare", {}).get("status") == "FAIL"

def test_adv_05_sentinel_log_spoofing_with_process_failure(temp_workspace):
    """ADV-05: If JVM crashes (rc != 0), Gate 2 fails closed even if log contains markers."""
    repo, out = temp_workspace
    p = Pipeline(repo, out)
    p.set_data("discover", {"entry": "TEST", "copybook_dirs": [], "file_ops": {}})
    p.set_data("baseline_files", ["data/out/report.txt"])
    
    mod_dir = os.path.join(out, "modernized")
    os.makedirs(os.path.join(mod_dir, "target"), exist_ok=True)
    jar_file = os.path.join(mod_dir, "target", "modernized-1.0.0.jar")
    with open(jar_file, "w") as f:
        f.write("dummy-jar")
        
    import unittest.mock as mock
    with mock.patch("shutil.which", return_value="fake_bin"), \
         mock.patch("cobol_migrate.sh", return_value=mock.Mock(returncode=0)), \
         mock.patch("subprocess.Popen") as mock_popen:
        
        proc_mock = mock.Mock()
        proc_mock.poll.return_value = 1  # JVM crashed with rc=1
        proc_mock.returncode = 1
        mock_popen.return_value = proc_mock
        
        success, msg, _ = p.stage_validate()
        assert not success
        assert "Spring Boot JVM exited with error (rc=1)" in msg
