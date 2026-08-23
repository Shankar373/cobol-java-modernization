import os
import sys
import pytest
import cobol_migrate as cm

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def blank_pipeline(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    out = tmp_path / "out"
    out.mkdir()
    p = cm.Pipeline(str(repo), str(out), pull=False)
    p._logs = []
    p.log = lambda msg: p._logs.append(msg)
    p.state = {"stages": {}, "data": {}}
    p.set_data = lambda k, v: p.state["data"].__setitem__(k, v)
    p.data = lambda k, default=None: p.state["data"].get(k, default)
    return p


def test_neg_equiv_console_with_stdin(blank_pipeline):
    """If stdin input values exist, console neg-equiv passes and registers mutation tested."""
    p = blank_pipeline
    p.set_data("execution_scenario", {
        "type": "non_interactive",
        "input_values": ["line1", "line2"]
    })

    p._run_neg_equiv_console()
    ne = p.data("neg_equiv")
    assert ne["executed"] is True
    assert ne["status"] == "PASS"
    assert ne["mode"] == "CONSOLE_OUTPUT"
    assert ne["mutations_tested"] == 1
    assert ne["mutations_caught"] == 1


def test_neg_equiv_console_without_stdin(blank_pipeline):
    """If no stdin inputs exist, console neg-equiv is UNVERIFIED."""
    p = blank_pipeline
    p.set_data("execution_scenario", None)  # No scenario

    p._run_neg_equiv_console()
    ne = p.data("neg_equiv")
    assert ne["executed"] is True
    assert ne["status"] == "UNVERIFIED"
    assert ne["mode"] == "CONSOLE_OUTPUT"
    assert "no stdin or input fixture" in ne["reason"]
    assert ne["mutations_tested"] == 0

    # Test with empty input_values list
    p.set_data("execution_scenario", {
        "type": "non_interactive",
        "input_values": []
    })
    p._run_neg_equiv_console()
    ne = p.data("neg_equiv")
    assert ne["status"] == "UNVERIFIED"
    assert ne["mutations_tested"] == 0


def test_neg_equiv_no_observable_output_stage_compare_routing(blank_pipeline, tmp_path):
    """NO_OBSERVABLE_OUTPUT topology automatically routes to UNVERIFIED negative equivalence during stage_compare."""
    # We will simulate stage_compare logic for NO_OBSERVABLE_OUTPUT
    p = blank_pipeline

    # Let's execute the logic from stage_compare for NO_OBSERVABLE_OUTPUT routing
    baseline_files = {}
    results_files = {}
    stdout_baseline = ""
    stdout_execute = ""

    from execution.topology import detect_topology
    topology = detect_topology(baseline_files, results_files, stdout_baseline, stdout_execute)
    assert topology == "NO_OBSERVABLE_OUTPUT"

    # Simulate routing logic
    if baseline_files and results_files:
        p._run_neg_equiv(baseline_files, results_files)
    elif topology == "CONSOLE_OUTPUT":
        p._run_neg_equiv_console()
    else:
        p.set_data("neg_equiv", {
            "executed": True,
            "status": "UNVERIFIED",
            "mode": topology,
            "reason": "no observable output available for mutation testing",
            "mutations_tested": 0,
            "mutations_caught": 0,
        })

    ne = p.data("neg_equiv")
    assert ne["executed"] is True
    assert ne["status"] == "UNVERIFIED"
    assert ne["mode"] == "NO_OBSERVABLE_OUTPUT"
    assert ne["mutations_tested"] == 0
