#!/usr/bin/env python3
"""
run_analysis_qpu.py — Evaluates IBM Marrakesh QPU execution results for Quantum Time Crystal Ring.
Uses the frozen count-based analyzer (src/analyzer.py) and computes comprehensive trajectories,
confidence intervals, and hypothesis tests.
"""

import json
from pathlib import Path
import numpy as np
import sys

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))
import analyzer

def main():
    print("=" * 70)
    print("GATE 8: QPU EXECUTION ANALYSIS — IBM MARRAKESH (HERON r2)")
    print("=" * 70)

    # 1. Load submission record and raw counts
    sub_file = list((REPO / "data" / "raw").glob("submission_record_*.json"))[0]
    raw_file = list((REPO / "data" / "raw").glob("raw_counts_*.json"))[0]

    with open(sub_file, encoding="utf-8") as f:
        sub_record = json.load(f)
    with open(raw_file, encoding="utf-8") as f:
        raw_data = json.load(f)

    job_id = sub_record["job_id"]
    order = sub_record["execution_order"]
    counts_list = raw_data["counts"]

    print(f"Loaded Job ID: {job_id}")
    print(f"Backend: {sub_record['backend']} | Circuits: {len(counts_list)}")

    # 2. Load pre-registered circuit table and parameters
    with open(REPO / "prereg" / "circuit_table.json", encoding="utf-8") as f:
        table = json.load(f)["circuits"]
    with open(REPO / "prereg" / "frozen_parameters.json", encoding="utf-8") as f:
        frozen_params = json.load(f)

    # Map raw counts back to pre-registered circuit table
    circuits_by_id = {}
    for k, orig_idx in enumerate(order):
        c_spec = table[orig_idx]
        cid = c_spec["circuit_id"]
        c_counts = counts_list[k]
        circuits_by_id[cid] = {
            "spec": c_spec,
            "counts": c_counts
        }

    # 3. Primary Hypothesis P1 Evaluation via Frozen Master Analyzer
    neel_12 = "010101010101"
    circ_J_tstar = circuits_by_id["CIRC_006"]["counts"]       # t=6, J=0.4
    circ_J_tp1 = circuits_by_id["CIRC_007"]["counts"]         # t=7, J=0.4
    circ_J0_tstar = circuits_by_id["CIRC_023"]["counts"]      # t=6, J=0.0
    circ_J0_tp1 = circuits_by_id["CIRC_024"]["counts"]        # t=7, J=0.0

    analyzer_input = {
        "t_star": 6,
        "initial_state": neel_12,
        "circuits": {
            "J_tstar": circ_J_tstar,
            "J_tstar_plus_1": circ_J_tp1,
            "J0_tstar": circ_J0_tstar,
            "J0_tstar_plus_1": circ_J0_tp1,
        }
    }

    print("\nRunning frozen master analyzer (P1 evaluation)...")
    res_p1 = analyzer.analyze_dataset(analyzer_input, n_boot=20000, seed=20261118)
    print(f"P1 Result: {json.dumps(res_p1, indent=2)}")

    # 4. Trajectory analysis: MAIN_J (t=0..16) vs CONTROL_J0 (t=0..16)
    main_j_traj = []
    for t in range(17):
        cid = f"CIRC_{t:03d}"
        c = circuits_by_id[cid]["counts"]
        m, site_z = analyzer.compute_m_and_d_from_counts(c, neel_12, 12)
        main_j_traj.append({
            "t": t,
            "circuit_id": cid,
            "m": float(m),
            "site_z": [float(x) for x in site_z]
        })

    control_j0_traj = []
    for t in range(17):
        cid = f"CIRC_{17 + t:03d}"
        c = circuits_by_id[cid]["counts"]
        m, site_z = analyzer.compute_m_and_d_from_counts(c, neel_12, 12)
        control_j0_traj.append({
            "t": t,
            "circuit_id": cid,
            "m": float(m),
            "site_z": [float(x) for x in site_z]
        })

    # Subharmonic order parameter S(t) = 0.5 * (m(t) - m(t+1))
    s_j_list = []
    s_j0_list = []
    contrast_list = []
    for t in range(16):
        s_j = 0.5 * (main_j_traj[t]["m"] - main_j_traj[t+1]["m"])
        s_j0 = 0.5 * (control_j0_traj[t]["m"] - control_j0_traj[t+1]["m"])
        s_j_list.append(s_j)
        s_j0_list.append(s_j0)
        contrast_list.append(abs(s_j) - abs(s_j0))

    # 5. P2: Gumicsere analysis (permutations 0, 3, 6, 9 at t=6 and t=7)
    gumicsere_specs = [
        (0, "CIRC_006", "CIRC_007"),
        (3, "CIRC_058", "CIRC_059"),
        (6, "CIRC_060", "CIRC_061"),
        (9, "CIRC_062", "CIRC_063")
    ]
    gumicsere_results = []
    for s_shift, cid_t, cid_tp1 in gumicsere_specs:
        c_t = circuits_by_id[cid_t]["counts"]
        c_tp1 = circuits_by_id[cid_tp1]["counts"]
        m_t, z_t = analyzer.compute_m_and_d_from_counts(c_t, neel_12, 12)
        m_tp1, z_tp1 = analyzer.compute_m_and_d_from_counts(c_tp1, neel_12, 12)
        s_val = 0.5 * (m_t - m_tp1)
        gumicsere_results.append({
            "shift": s_shift,
            "cid_t": cid_t,
            "cid_tp1": cid_tp1,
            "m_t": float(m_t),
            "m_tp1": float(m_tp1),
            "s_val": float(s_val),
            "site_z_t": [float(x) for x in z_t]
        })

    gumicsere_s_vals = [r["s_val"] for r in gumicsere_results]
    gumicsere_var = float(np.var(gumicsere_s_vals))
    print(f"\nP2 (Gumicsere) S-values across shifts [0, 3, 6, 9]: {[round(x, 4) for x in gumicsere_s_vals]}")
    print(f"Variance across disorder shifts: {gumicsere_var:.6f}")

    # 6. P3: Epsilon sweep (eps = 0.0, 0.03, 0.06, 0.10, 0.15, 0.20)
    eps_specs = [
        (0.0,  "CIRC_038", "CIRC_039", "CIRC_040", "CIRC_041"),
        (0.03, "CIRC_042", "CIRC_043", "CIRC_044", "CIRC_045"),
        (0.06, "CIRC_046", "CIRC_047", "CIRC_048", "CIRC_049"),
        (0.10, "CIRC_006", "CIRC_007", "CIRC_023", "CIRC_024"),
        (0.15, "CIRC_050", "CIRC_051", "CIRC_052", "CIRC_053"),
        (0.20, "CIRC_054", "CIRC_055", "CIRC_056", "CIRC_057"),
    ]
    eps_results = []
    for eps_val, cid_j_t, cid_j_tp1, cid_j0_t, cid_j0_tp1 in eps_specs:
        c_jt = circuits_by_id[cid_j_t]["counts"]
        c_jtp1 = circuits_by_id[cid_j_tp1]["counts"]
        c_j0t = circuits_by_id[cid_j0_t]["counts"]
        c_j0tp1 = circuits_by_id[cid_j0_tp1]["counts"]

        m_jt, _ = analyzer.compute_m_and_d_from_counts(c_jt, neel_12, 12)
        m_jtp1, _ = analyzer.compute_m_and_d_from_counts(c_jtp1, neel_12, 12)
        s_j_val = 0.5 * (m_jt - m_jtp1)

        m_j0t, _ = analyzer.compute_m_and_d_from_counts(c_j0t, neel_12, 12)
        m_j0tp1, _ = analyzer.compute_m_and_d_from_counts(c_j0tp1, neel_12, 12)
        s_j0_val = 0.5 * (m_j0t - m_j0tp1)

        eps_results.append({
            "eps": eps_val,
            "s_j": float(s_j_val),
            "s_j0": float(s_j0_val),
            "contrast": float(abs(s_j_val) - abs(s_j0_val))
        })

    print("\nP3 (Eps sweep):")
    for r in eps_results:
        print(f"  eps={r['eps']:4.2f} | S_J={r['s_j']:+.4f} | S_J0={r['s_j0']:+.4f} | Contrast={r['contrast']:+.4f}")

    # 7. Triangle module analysis
    # CIRC_079/080: triangle_3q (closed ring), CIRC_081/082: open path 3q, CIRC_083/084: triangle J=0
    neel_3 = "010"
    tri_results = {}
    for name, cid_t, cid_tp1 in [
        ("closed_ring_3q", "CIRC_079", "CIRC_080"),
        ("open_path_3q", "CIRC_081", "CIRC_082"),
        ("triangle_j0_3q", "CIRC_083", "CIRC_084")
    ]:
        c_t = circuits_by_id[cid_t]["counts"]
        c_tp1 = circuits_by_id[cid_tp1]["counts"]
        m_t, z_t = analyzer.compute_m_and_d_from_counts(c_t, neel_3, 3)
        m_tp1, z_tp1 = analyzer.compute_m_and_d_from_counts(c_tp1, neel_3, 3)
        s_val = 0.5 * (m_t - m_tp1)
        tri_results[name] = {
            "m_t": float(m_t),
            "m_tp1": float(m_tp1),
            "s_val": float(s_val),
            "site_z_t": [float(x) for x in z_t]
        }
    print(f"\nTriangle Module Results at t*=6:")
    for k, v in tri_results.items():
        print(f"  {k}: S = {v['s_val']:+.4f} (m(6)={v['m_t']:+.4f}, m(7)={v['m_tp1']:+.4f})")

    # 8. Intra-job drift test: CIRC_006, CIRC_072, CIRC_073, CIRC_074
    drift_circs = ["CIRC_006", "CIRC_072", "CIRC_073", "CIRC_074"]
    drift_vals = []
    for cid in drift_circs:
        c = circuits_by_id[cid]["counts"]
        m, _ = analyzer.compute_m_and_d_from_counts(c, neel_12, 12)
        drift_vals.append((cid, float(m)))
    print(f"\nIntra-job drift at t=6: {[(cid, round(m, 4)) for cid, m in drift_vals]}")
    drift_std = float(np.std([m for _, m in drift_vals]))
    print(f"Drift std across 4 replicates: {drift_std:.4f}")

    # 9. Comparison against 3 Predictions
    # Column 1: Máté's prediction (discovery hypothesis: ring protection exceeds noisy Aer)
    # Column 2: Standard physics / Aer Noisy simulation prediction
    # Column 3: Raw QPU execution
    with open(REPO / "sim" / "noisy" / "noisy_aer_predictions.json", encoding="utf-8") as f:
        aer_pred = json.load(f)
    with open(REPO / "sim" / "ideal" / "ideal_predictions.json", encoding="utf-8") as f:
        ideal_pred = json.load(f)

    # Compile comprehensive final report
    final_report = {
        "job_id": job_id,
        "backend": sub_record["backend"],
        "shots_per_circuit": sub_record["shots"],
        "total_circuits": len(counts_list),
        "analyzer_p1": res_p1["P1"],
        "t_star": 6,
        "s_J_at_tstar": round(float(abs(s_j_list[6])), 4),
        "s_J0_at_tstar": round(float(abs(s_j0_list[6])), 4),
        "contrast_at_tstar": round(float(contrast_list[6]), 4),
        "three_column_comparison": {
            "metric": "Contrast |S_J(6)| - |S_J0(6)|",
            "column_1_mate_hypothesis": "Protection exceeds Aer noisy model (> +0.66)",
            "column_2_theory_ideal": round(ideal_pred["predictions_table_col2"]["P1_interaction_protection_s_diff"], 4),
            "column_2_aer_noisy": round(aer_pred["predictions_table_col3"]["P1_interaction_protection_s_diff"], 4),
            "column_3_qpu_actual": round(float(contrast_list[6]), 4),
            "ci99_qpu": res_p1["P1"]["ci99"]
        },
        "gumicsere": {
            "results": gumicsere_results,
            "variance": gumicsere_var
        },
        "eps_sweep": eps_results,
        "triangle_module": tri_results,
        "intra_job_drift": {
            "replicates": drift_vals,
            "std": drift_std
        },
        "trajectories": {
            "main_j": main_j_traj,
            "control_j0": control_j0_traj,
            "s_j": [float(x) for x in s_j_list],
            "s_j0": [float(x) for x in s_j0_list],
            "contrast": [float(x) for x in contrast_list]
        }
    }

    out_path = REPO / "results" / "qpu_analysis_report.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(final_report, f, indent=2)

    print(f"\nSaved comprehensive QPU report to: {out_path}")

if __name__ == "__main__":
    main()
