#!/usr/bin/env python3
"""
test_qpu_analysis.py — Automated verification of Gate 8 analysis of ibm_marrakesh QPU execution.
"""

import json
from pathlib import Path
import pytest
import numpy as np

REPO = Path(__file__).resolve().parent.parent

@pytest.fixture(scope="module")
def qpu_report():
    report_file = REPO / "results" / "qpu_analysis_report.json"
    assert report_file.exists(), "qpu_analysis_report.json missing!"
    with open(report_file, encoding="utf-8") as f:
        return json.load(f)

def test_p1_verdict(qpu_report):
    p1 = qpu_report["analyzer_p1"]
    assert p1["verdict"] == "SUPPORTED"
    assert p1["point_diff"] > p1["delta_min"]
    assert p1["ci99"][0] > 0.0
    assert p1["p_value_one_sided"] < 0.0033

def test_three_column_comparison(qpu_report):
    comp = qpu_report["three_column_comparison"]
    ideal = comp["column_2_theory_ideal"]
    aer = comp["column_2_aer_noisy"]
    qpu = comp["column_3_qpu_actual"]
    assert ideal > aer > qpu > 0.0
    # QPU is positive, confirming DTC, but lower than Aer due to real device noise
    assert qpu > 0.50

def test_p2_gumicsere_invariance(qpu_report):
    gumicsere = qpu_report["gumicsere"]
    var = gumicsere["variance"]
    # Disorder shift variance should be low (< 0.001)
    assert var < 0.001
    s_vals = [r["s_val"] for r in gumicsere["results"]]
    assert all(s > 0.60 for s in s_vals)

def test_trajectories_period_doubling(qpu_report):
    s_j = qpu_report["trajectories"]["s_j"]
    s_j0 = qpu_report["trajectories"]["s_j0"]
    # S_J should maintain period-doubling sign pattern (+, -, +, -, ...)
    # which means s_j alternate sign
    for t in range(len(s_j)):
        expected_sign = 1 if t % 2 == 0 else -1
        assert (s_j[t] * expected_sign) > 0, f"Period doubling lost in S_J at t={t}"

    # Non-interacting S_J0 must flip sign due to eps=0.10 beat frequency around t=8
    # At t=8, expected_sign is +1, but S_J0 flips to negative
    assert s_j0[8] < 0.0, "J0 did not experience beat frequency phase flip!"
