#!/usr/bin/env python3
"""
generate_circuit_table.py — Master circuit table generator and parameter freezer
Gate 5 of Quantum Time Crystal Ring protocol.
"""

import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

def build_circuit_table():
    circuits = []
    c_idx = 0

    J_nominal = 0.4
    W_nominal = 1.5
    eps0 = 0.10
    t_star = 6
    T = 16
    neel = "010101010101"
    disorder_seed = 20261118

    # 1. Main J Branch (t = 0..T)
    for t in range(T + 1):
        circuits.append({
            "circuit_id": f"CIRC_{c_idx:03d}",
            "block": "MAIN_J",
            "geometry": "ring_12q",
            "t_cycles": t,
            "eps": eps0,
            "J": J_nominal,
            "W": W_nominal,
            "initial_state": neel,
            "permutation_shift": 0,
            "is_echo": False,
            "expected_cz_count": 12 * t
        })
        c_idx += 1

    # 2. Control J=0 Branch (t = 0..T, duration matched)
    for t in range(T + 1):
        circuits.append({
            "circuit_id": f"CIRC_{c_idx:03d}",
            "block": "CONTROL_J0",
            "geometry": "ring_12q",
            "t_cycles": t,
            "eps": eps0,
            "J": 0.0,
            "W": W_nominal,
            "initial_state": neel,
            "permutation_shift": 0,
            "is_echo": False,
            "expected_cz_count": 0
        })
        c_idx += 1

    # 3. Control W=0 Branch (t*, t*+1, T-1, T)
    for t in [t_star, t_star + 1, T - 1, T]:
        circuits.append({
            "circuit_id": f"CIRC_{c_idx:03d}",
            "block": "CONTROL_W0",
            "geometry": "ring_12q",
            "t_cycles": t,
            "eps": eps0,
            "J": J_nominal,
            "W": 0.0,
            "initial_state": neel,
            "permutation_shift": 0,
            "is_echo": False,
            "expected_cz_count": 12 * t
        })
        c_idx += 1

    # 4. Epsilon Sweep (6 values x [J, J=0] x [t*, t*+1])
    eps_grid = [0.0, 0.03, 0.06, 0.10, 0.15, 0.20]
    for eps in eps_grid:
        for is_j0 in [False, True]:
            for t in [t_star, t_star + 1]:
                # Skip duplicate of main branch at eps0
                if eps == eps0 and t in [t_star, t_star + 1]:
                    continue
                circuits.append({
                    "circuit_id": f"CIRC_{c_idx:03d}",
                    "block": "EPS_SWEEP",
                    "geometry": "ring_12q",
                    "t_cycles": t,
                    "eps": eps,
                    "J": 0.0 if is_j0 else J_nominal,
                    "W": W_nominal,
                    "initial_state": neel,
                    "permutation_shift": 0,
                    "is_echo": False,
                    "expected_cz_count": 0 if is_j0 else 12 * t
                })
                c_idx += 1

    # 5. Gumicsere Rotational Permutation (3 shifts x [t*, t*+1])
    for shift in [3, 6, 9]:
        for t in [t_star, t_star + 1]:
            circuits.append({
                "circuit_id": f"CIRC_{c_idx:03d}",
                "block": "GUMICSERE_PERM",
                "geometry": "ring_12q",
                "t_cycles": t,
                "eps": eps0,
                "J": J_nominal,
                "W": W_nominal,
                "initial_state": neel,
                "permutation_shift": shift,
                "is_echo": False,
                "expected_cz_count": 12 * t
            })
            c_idx += 1

    # 6. Time-Reversal Echo Branch
    for t in [2, 4, 6, 8]:
        circuits.append({
            "circuit_id": f"CIRC_{c_idx:03d}",
            "block": "ECHO",
            "geometry": "ring_12q",
            "t_cycles": t,
            "eps": eps0,
            "J": J_nominal,
            "W": W_nominal,
            "initial_state": neel,
            "permutation_shift": 0,
            "is_echo": True,
            "expected_cz_count": 24 * t
        })
        c_idx += 1

    # 7. Additional Initial States (Random 1 & 2 x [t*, t*+1])
    rand_states = ["110100101011", "001101100101"]
    for r_state in rand_states:
        for t in [t_star, t_star + 1]:
            circuits.append({
                "circuit_id": f"CIRC_{c_idx:03d}",
                "block": "INITIAL_STATES",
                "geometry": "ring_12q",
                "t_cycles": t,
                "eps": eps0,
                "J": J_nominal,
                "W": W_nominal,
                "initial_state": r_state,
                "permutation_shift": 0,
                "is_echo": False,
                "expected_cz_count": 12 * t
            })
            c_idx += 1

    # 8. Intra-Job Temporal Drift Control (repeat main t* at start, middle, end)
    for rep in [1, 2, 3]:
        circuits.append({
            "circuit_id": f"CIRC_{c_idx:03d}",
            "block": "INTRA_JOB_DRIFT",
            "geometry": "ring_12q",
            "t_cycles": t_star,
            "eps": eps0,
            "J": J_nominal,
            "W": W_nominal,
            "initial_state": neel,
            "permutation_shift": 0,
            "is_echo": False,
            "expected_cz_count": 12 * t_star,
            "repeat_tag": f"drift_repeat_{rep}"
        })
        c_idx += 1

    # 9. In-Situ Readout Calibration (4 states: 0^12, 1^12, 2 random)
    ro_states = ["000000000000", "111111111111", "101001101001", "010110010110"]
    for ro_state in ro_states:
        circuits.append({
            "circuit_id": f"CIRC_{c_idx:03d}",
            "block": "READOUT_CALIB",
            "geometry": "ring_12q",
            "t_cycles": 0,
            "eps": 0.0,
            "J": 0.0,
            "W": 0.0,
            "initial_state": ro_state,
            "permutation_shift": 0,
            "is_echo": False,
            "expected_cz_count": 0
        })
        c_idx += 1

    # 10. Triangle Module ([triangle, open path, triangle J=0] x [t*, t*+1])
    for geom in ["triangle_3q", "open_path_3q", "triangle_j0_3q"]:
        for t in [t_star, t_star + 1]:
            cz_per_cycle = 9 if geom == "triangle_3q" else (4 if geom == "open_path_3q" else 0)
            circuits.append({
                "circuit_id": f"CIRC_{c_idx:03d}",
                "block": "TRIANGLE_MODULE",
                "geometry": geom,
                "t_cycles": t,
                "eps": eps0,
                "J": 0.0 if geom == "triangle_j0_3q" else J_nominal,
                "W": W_nominal,
                "initial_state": "010",
                "permutation_shift": 0,
                "is_echo": False,
                "expected_cz_count": cz_per_cycle * t
            })
            c_idx += 1

    return circuits

def main():
    circuits = build_circuit_table()
    print(f"Total compiled pre-registered circuits: {len(circuits)}")

    prereg_dir = REPO / "prereg"
    prereg_dir.mkdir(parents=True, exist_ok=True)

    table_file = prereg_dir / "circuit_table.json"
    with open(table_file, "w", encoding="utf-8") as f:
        json.dump({"total_circuits": len(circuits), "circuits": circuits}, f, indent=2)
    print(f"Saved circuit table to: {table_file}")

    # Frozen parameters card
    params_card = {
        "hardware_target": "ibm_marrakesh (Heron r2, 156Q)",
        "authorized_deviation": "DEV-001 (by Máté Róbert)",
        "selected_12_ring_qubits": [131, 132, 133, 134, 135, 139, 155, 154, 153, 152, 151, 138],
        "selected_3_triangle_qubits": [151, 138, 131],
        "nominal_J": 0.4,
        "nominal_W": 1.5,
        "nominal_eps0": 0.10,
        "t_star": 6,
        "T_max": 16,
        "shots_per_circuit": 2048,
        "familywise_alpha": 0.01,
        "delta_min": 0.05,
        "disorder_seed": 20261118,
        "shuffle_seed": 20261119,
        "bootstrap_seed": 20261120,
        "total_circuits_count": len(circuits),
        "status": "FROZEN_FOR_PREREGISTRATION"
    }
    params_file = prereg_dir / "frozen_parameters.json"
    with open(params_file, "w", encoding="utf-8") as f:
        json.dump(params_card, f, indent=2)
    print(f"Saved frozen parameters to: {params_file}")

    # Compute master SHA256 hashes
    def get_sha256(path: Path) -> str:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    plan_sha256 = get_sha256(REPO / "docs" / "PLAN_v1.0.md")
    analyzer_sha256 = get_sha256(REPO / "src" / "analyzer.py")
    table_sha256 = get_sha256(table_file)
    params_sha256 = get_sha256(params_file)
    predictions_sha256 = get_sha256(REPO / "docs" / "PREDICTIONS.md")

    hash_card = {
        "preregistration_status": "FROZEN",
        "date_utc": "2026-11-18T18:18:00Z",
        "date_budapest": "2026-11-18T19:18:00+01:00",
        "hashes": {
            "docs/PLAN_v1.0.md": plan_sha256,
            "docs/PREDICTIONS.md": predictions_sha256,
            "src/analyzer.py": analyzer_sha256,
            "prereg/circuit_table.json": table_sha256,
            "prereg/frozen_parameters.json": params_sha256
        }
    }
    hash_file = prereg_dir / "hash_card.json"
    with open(hash_file, "w", encoding="utf-8") as f:
        json.dump(hash_card, f, indent=2)
    print(f"Saved master hash card to: {hash_file}")

if __name__ == "__main__":
    main()
