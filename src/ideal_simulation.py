#!/usr/bin/env python3
"""
ideal_simulation.py — Exact classical unitary statevector simulation (Gate 2)
Computes Floquet period-doubling dynamics for 12-qubit ring and 3-qubit triangle.
All outputs are strictly tagged [SZIMULÁCIÓ].
"""

import json
import math
from pathlib import Path
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

REPO = Path(__file__).resolve().parent.parent

def precompute_z_vals(num_qubits: int):
    dim = 2 ** num_qubits
    indices = np.arange(dim)
    bits = (indices[:, None] >> np.arange(num_qubits)) & 1
    return 1 - 2 * bits  # shape (dim, num_qubits)

def simulate_floquet_dynamics(
    num_qubits: int,
    edges: list[tuple[int, int]],
    initial_bitstring: str,
    eps: float,
    J: float,
    W: float,
    disorder_seed: int,
    T: int
):
    """
    Simulates T Floquet cycles.
    Returns:
      m: list of length T+1 (normalized magnetization relative to initial state)
      S: list of length T (subharmonic amplitude S(t) = 0.5 * (m(t) - m(t+1)))
    """
    dim = 2 ** num_qubits
    z_basis_vals = precompute_z_vals(num_qubits)
    
    # Initial state
    qc_init = QuantumCircuit(num_qubits)
    init_bits = [int(b) for b in initial_bitstring[::-1]]  # Qiskit qubit 0 is rightmost in bitstring
    for i, b in enumerate(init_bits):
        if b == 1:
            qc_init.x(i)
    
    # Initial z_i(0) values
    z0 = np.array([1 - 2 * b for b in init_bits], dtype=float)
    
    # Sample disorder fields
    rng = np.random.default_rng(disorder_seed)
    h = rng.uniform(-W, W, num_qubits) if W > 0 else np.zeros(num_qubits)
    
    # Pre-build 1 Floquet cycle circuit
    cycle_qc = QuantumCircuit(num_qubits)
    # 1. Pulse layer
    cycle_qc.rx(np.pi * (1.0 - eps), range(num_qubits))
    # 2. Interaction layer
    if J > 0:
        for u, v in edges:
            cycle_qc.rzz(2 * J, u, v)
    # 3. Disorder layer
    if W > 0:
        for i in range(num_qubits):
            cycle_qc.rz(2 * h[i], i)
            
    sv = Statevector.from_instruction(qc_init)
    
    m_list = []
    # t = 0
    probs = np.abs(sv.data) ** 2
    exp_z = probs @ z_basis_vals  # shape (num_qubits,)
    m0 = float(np.mean(z0 * exp_z))
    m_list.append(m0)
    
    for t in range(1, T + 1):
        sv = sv.evolve(cycle_qc)
        probs = np.abs(sv.data) ** 2
        exp_z = probs @ z_basis_vals
        mt = float(np.mean(z0 * exp_z))
        m_list.append(mt)
        
    # Subharmonic observable S(t) = 0.5 * (m(t) - m(t+1))
    s_list = [0.5 * (m_list[t] - m_list[t + 1]) for t in range(T)]
    
    return m_list, s_list

def run_parameter_sweep():
    num_qubits = 12
    edges_ring = [(i, (i + 1) % num_qubits) for i in range(num_qubits)]
    
    initial_states = {
        "neel": "010101010101",
        "random1": "110100101011",
        "random2": "001101100101"
    }
    
    J_values = [0.0, 0.2, 0.4, 0.6, 0.8]
    W_values = [0.0, 0.5, 1.0, 1.5]
    eps_values = [0.0, 0.03, 0.06, 0.10, 0.15, 0.20]
    T = 16
    seed = 20261118
    
    sweep_results = []
    
    print("Running parameter sweep over J, W, eps (12-qubit ring)...")
    for J in J_values:
        for W in W_values:
            for eps in eps_values:
                # Evaluate on Neel state
                m_neel, s_neel = simulate_floquet_dynamics(
                    num_qubits, edges_ring, initial_states["neel"], eps, J, W, seed, T
                )
                
                # S at t=6 (midpoint) and t=12
                s_mid = abs(s_neel[6])
                s_late = abs(s_neel[12])
                
                sweep_results.append({
                    "J": J,
                    "W": W,
                    "eps": eps,
                    "s_mid": round(s_mid, 4),
                    "s_late": round(s_late, 4),
                    "m_traj": [round(x, 4) for x in m_neel],
                    "s_traj": [round(x, 4) for x in s_neel]
                })
                
    return sweep_results

def select_optimal_parameters(sweep_results):
    """
    Selection rule from Section 4.1:
    Find (J, W, eps0) where:
    - At J > 0, period doubling persists (S(t) remains high up to T)
    - At J = 0, period doubling collapses (S(t) beat/decay is rapid)
    - Maximizes contrast: S_J(t*) - S_J=0(t*) at eps0
    """
    # Fix t* = 6
    best_candidate = None
    max_contrast = -1.0
    
    for r in sweep_results:
        if r["J"] > 0 and r["W"] > 0 and r["eps"] in [0.06, 0.10]:
            # Find matching J=0 reference
            matching_j0 = next(
                (x for x in sweep_results if x["J"] == 0.0 and x["W"] == r["W"] and x["eps"] == r["eps"]),
                None
            )
            if matching_j0:
                contrast = abs(r["s_mid"]) - abs(matching_j0["s_mid"])
                if contrast > max_contrast:
                    max_contrast = contrast
                    best_candidate = {
                        "J": r["J"],
                        "W": r["W"],
                        "eps0": r["eps"],
                        "t_star": 6,
                        "T": 16,
                        "contrast": round(contrast, 4),
                        "s_J_tstar": abs(r["s_mid"]),
                        "s_J0_tstar": abs(matching_j0["s_mid"])
                    }
    return best_candidate

def compute_all_standard_predictions(best_params):
    J = best_params["J"]
    W = best_params["W"]
    eps0 = best_params["eps0"]
    t_star = best_params["t_star"]
    T = best_params["T"]
    seed = 20261118
    
    # 1. 12-qubit ring
    num_ring = 12
    edges_ring = [(i, (i + 1) % num_ring) for i in range(num_ring)]
    
    # Primary J branch
    m_J, s_J = simulate_floquet_dynamics(num_ring, edges_ring, "010101010101", eps0, J, W, seed, T)
    # Control J=0 branch
    m_J0, s_J0 = simulate_floquet_dynamics(num_ring, edges_ring, "010101010101", eps0, 0.0, W, seed, T)
    # Control W=0 branch
    m_W0, s_W0 = simulate_floquet_dynamics(num_ring, edges_ring, "010101010101", eps0, J, 0.0, seed, T)
    
    # P1 prediction
    p1_diff = abs(s_J[t_star]) - abs(s_J0[t_star])
    
    # Beat frequency of J=0 branch
    # Analytical: in absence of interaction, spins precess by eps * pi per cycle, beat frequency = eps
    # Let's do FFT of m_J0
    fft_m = np.abs(np.fft.rfft(m_J0))
    freqs = np.fft.rfftfreq(len(m_J0))
    peak_idx = np.argmax(fft_m[1:]) + 1
    measured_peak_freq = float(freqs[peak_idx])
    
    # 2. 3-qubit triangle vs open path
    edges_tri = [(0, 1), (1, 2), (2, 0)]
    edges_path = [(0, 1), (1, 2)]
    m_tri, s_tri = simulate_floquet_dynamics(3, edges_tri, "010", eps0, J, W, seed, T)
    m_path, s_path = simulate_floquet_dynamics(3, edges_path, "010", eps0, J, W, seed, T)
    tri_path_diff = abs(s_tri[t_star]) - abs(s_path[t_star])
    
    # eps-sweep half-survival points
    eps_grid = [0.0, 0.03, 0.06, 0.10, 0.15, 0.20]
    s_at_tstar_J = []
    s_at_tstar_J0 = []
    for eps in eps_grid:
        _, s_cur_J = simulate_floquet_dynamics(num_ring, edges_ring, "010101010101", eps, J, W, seed, T)
        _, s_cur_J0 = simulate_floquet_dynamics(num_ring, edges_ring, "010101010101", eps, 0.0, W, seed, T)
        s_at_tstar_J.append(abs(s_cur_J[t_star]))
        s_at_tstar_J0.append(abs(s_cur_J0[t_star]))
        
    # Interpolate eps_half
    s0_J = s_at_tstar_J[0]
    s0_J0 = s_at_tstar_J0[0]
    eps_half_J = float(np.interp(s0_J / 2.0, s_at_tstar_J[::-1], eps_grid[::-1]))
    eps_half_J0 = float(np.interp(s0_J0 / 2.0, s_at_tstar_J0[::-1], eps_grid[::-1]))
    delta_eps_half = eps_half_J - eps_half_J0
    
    predictions = {
        "metadata": {
            "type": "SZIMULÁCIÓ",
            "model": "Exact Unitary Statevector (Schrödinger Evolution)",
            "date_utc": "2026-11-18T17:52:00Z",
            "date_budapest": "2026-11-18T18:52:00+01:00",
            "software": "Qiskit / NumPy Statevector"
        },
        "chosen_parameters": {
            "J": J,
            "W": W,
            "eps0": eps0,
            "t_star": t_star,
            "T": T,
            "eps_grid": eps_grid,
            "disorder_seed": seed,
            "initial_state_neel": "010101010101"
        },
        "predictions_table_col2": {
            "P1_interaction_protection_s_diff": round(float(p1_diff), 4),
            "s_J_at_tstar": round(float(abs(s_J[t_star])), 4),
            "s_J0_at_tstar": round(float(abs(s_J0[t_star])), 4),
            "P2_gumicsere_governing_factor": "LOGICAL DISORDER SITE GOVERNS (In ideal simulation, physical layout has zero defect variation)",
            "P3_delta_eps_half": round(float(delta_eps_half), 4),
            "eps_half_J": round(float(eps_half_J), 4),
            "eps_half_J0": round(float(eps_half_J0), 4),
            "J0_beat_frequency_analytical": round(float(eps0), 4),
            "J0_spectral_peak_freq": round(float(measured_peak_freq), 4),
            "disorder_effect_W_vs_W0_diff": round(float(abs(s_J[t_star]) - abs(s_W0[t_star])), 4),
            "triangle_vs_open_path_diff": round(float(tri_path_diff), 4),
            "decoherence_echo_floor_E_tstar": 1.0000
        },
        "trajectories": {
            "s_J": [round(float(x), 4) for x in s_J],
            "s_J0": [round(float(x), 4) for x in s_J0],
            "s_W0": [round(float(x), 4) for x in s_W0],
            "s_tri": [round(float(x), 4) for x in s_tri],
            "s_path": [round(float(x), 4) for x in s_path]
        }
    }
    return predictions

def main():
    print("=" * 70)
    print("GATE 2: IDEAL SIMULATION & PARAMETER SELECTION [SZIMULÁCIÓ]")
    print("=" * 70)
    
    sweep_results = run_parameter_sweep()
    best_candidate = select_optimal_parameters(sweep_results)
    
    print("\nOptimal Parameter Selection:")
    print(f"  J = {best_candidate['J']}")
    print(f"  W = {best_candidate['W']}")
    print(f"  eps0 = {best_candidate['eps0']}")
    print(f"  t* = {best_candidate['t_star']}")
    print(f"  T = {best_candidate['T']}")
    print(f"  Max contrast |S_J(t*)| - |S_J=0(t*)| = {best_candidate['contrast']}")
    
    preds = compute_all_standard_predictions(best_candidate)
    
    sim_dir = REPO / "sim" / "ideal"
    sim_dir.mkdir(parents=True, exist_ok=True)
    
    sweep_file = sim_dir / "parameter_sweep.json"
    with open(sweep_file, "w", encoding="utf-8") as f:
        json.dump({"type": "SZIMULÁCIÓ", "sweep": sweep_results}, f, indent=2)
    print(f"Saved parameter sweep to: {sweep_file}")
    
    preds_file = sim_dir / "ideal_predictions.json"
    with open(preds_file, "w", encoding="utf-8") as f:
        json.dump(preds, f, indent=2)
    print(f"Saved ideal predictions to: {preds_file}")

if __name__ == "__main__":
    main()
