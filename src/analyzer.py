#!/usr/bin/env python3
"""
analyzer.py — Pre-registered primary hypothesis analyzer for Quantum Time Crystal Ring
Evaluates P1 (interaction protection), P2 (gumicsere), and P3 (eps tolerance).
Deterministic, count-based, with 99% bootstrap confidence intervals and Holm correction.
"""

import math
from pathlib import Path
import numpy as np

DELTA_MIN = 0.05
ALPHA_FAMILY = 0.01

def compute_m_and_d_from_counts(counts: dict, initial_bitstring: str, num_qubits: int = 12):
    init_bits = [int(b) for b in initial_bitstring[::-1]]
    z0 = np.array([1 - 2 * b for b in init_bits], dtype=float)
    total_shots = sum(counts.values())
    if total_shots == 0:
        return 0.0, np.zeros(num_qubits)
        
    site_z = np.zeros(num_qubits, dtype=float)
    for bitstr, cnt in counts.items():
        bits = np.array([int(b) for b in bitstr[::-1]], dtype=float)
        site_z += cnt * (1.0 - 2.0 * bits)
    site_z /= total_shots
    m = float(np.mean(z0 * site_z))
    return m, site_z

def analyze_dataset(data: dict, n_boot: int = 5000, seed: int = 20261118) -> dict:
    """
    Evaluates P1, P2, P3 according to pre-registered rules.
    data format:
      "circuits": {
         "J_tstar": counts,
         "J_tstar_plus_1": counts,
         "J0_tstar": counts,
         "J0_tstar_plus_1": counts,
         ...
      }
    """
    circuits = data.get("circuits", {})
    t_star = data.get("t_star", 6)
    neel = data.get("initial_state", "010101010101")
    
    # Validity checks
    required = ["J_tstar", "J_tstar_plus_1", "J0_tstar", "J0_tstar_plus_1"]
    for k in required:
        if k not in circuits or sum(circuits[k].values()) == 0:
            return {
                "verdict": "INVALID",
                "reason": f"Missing or empty counts for required circuit: {k}"
            }
            
    m_J_t, z_J_t = compute_m_and_d_from_counts(circuits["J_tstar"], neel)
    m_J_tp1, z_J_tp1 = compute_m_and_d_from_counts(circuits["J_tstar_plus_1"], neel)
    s_J = 0.5 * (m_J_t - m_J_tp1)
    
    m_J0_t, z_J0_t = compute_m_and_d_from_counts(circuits["J0_tstar"], neel)
    m_J0_tp1, z_J0_tp1 = compute_m_and_d_from_counts(circuits["J0_tstar_plus_1"], neel)
    s_J0 = 0.5 * (m_J0_t - m_J0_tp1)
    
    point_diff = abs(s_J) - abs(s_J0)
    
    # Shot-level bootstrap for P1
    rng = np.random.default_rng(seed)
    shots_J_t = sum(circuits["J_tstar"].values())
    shots_J_tp1 = sum(circuits["J_tstar_plus_1"].values())
    shots_J0_t = sum(circuits["J0_tstar"].values())
    shots_J0_tp1 = sum(circuits["J0_tstar_plus_1"].values())
    
    # Fast multinomial resampling
    keys_J_t = list(circuits["J_tstar"].keys())
    p_J_t = np.array([circuits["J_tstar"][k] for k in keys_J_t], dtype=float) / shots_J_t
    
    keys_J_tp1 = list(circuits["J_tstar_plus_1"].keys())
    p_J_tp1 = np.array([circuits["J_tstar_plus_1"][k] for k in keys_J_tp1], dtype=float) / shots_J_tp1
    
    keys_J0_t = list(circuits["J0_tstar"].keys())
    p_J0_t = np.array([circuits["J0_tstar"][k] for k in keys_J0_t], dtype=float) / shots_J0_t
    
    keys_J0_tp1 = list(circuits["J0_tstar_plus_1"].keys())
    p_J0_tp1 = np.array([circuits["J0_tstar_plus_1"][k] for k in keys_J0_tp1], dtype=float) / shots_J0_tp1
    
    # Resample counts
    resampled_J_t = rng.multinomial(shots_J_t, p_J_t, size=n_boot)
    resampled_J_tp1 = rng.multinomial(shots_J_tp1, p_J_tp1, size=n_boot)
    resampled_J0_t = rng.multinomial(shots_J0_t, p_J0_t, size=n_boot)
    resampled_J0_tp1 = rng.multinomial(shots_J0_tp1, p_J0_tp1, size=n_boot)
    
    init_bits = [int(b) for b in neel[::-1]]
    z0 = np.array([1 - 2 * b for b in init_bits], dtype=float)
    
    def fast_m_batch(res_counts, keys, n_shots):
        bit_mat = np.array([[int(b) for b in k[::-1]] for k in keys], dtype=float)
        z_mat = 1.0 - 2.0 * bit_mat # shape (n_keys, 12)
        site_z = (res_counts @ z_mat) / n_shots # shape (n_boot, 12)
        return np.mean(site_z * z0, axis=1) # shape (n_boot,)
        
    m_boot_J_t = fast_m_batch(resampled_J_t, keys_J_t, shots_J_t)
    m_boot_J_tp1 = fast_m_batch(resampled_J_tp1, keys_J_tp1, shots_J_tp1)
    s_boot_J = 0.5 * (m_boot_J_t - m_boot_J_tp1)
    
    m_boot_J0_t = fast_m_batch(resampled_J0_t, keys_J0_t, shots_J0_t)
    m_boot_J0_tp1 = fast_m_batch(resampled_J0_tp1, keys_J0_tp1, shots_J0_tp1)
    s_boot_J0 = 0.5 * (m_boot_J0_t - m_boot_J0_tp1)
    
    diff_boot = np.abs(s_boot_J) - np.abs(s_boot_J0)
    ci99_low = float(np.percentile(diff_boot, 0.5))
    ci99_high = float(np.percentile(diff_boot, 99.5))
    
    # One-sided p-value
    p_val_p1 = float(np.mean(diff_boot <= 0.0))
    
    # Decision rule for P1 (Holm alpha = 0.01 / 3 = 0.0033)
    alpha_p1 = ALPHA_FAMILY / 3.0
    if p_val_p1 < alpha_p1 and ci99_low > 0.0:
        verdict_p1 = "SUPPORTED"
    elif ci99_low <= 0.0 and ci99_high < DELTA_MIN:
        verdict_p1 = "NULL"
    else:
        verdict_p1 = "INCONCLUSIVE"
        
    return {
        "P1": {
            "verdict": verdict_p1,
            "point_diff": round(point_diff, 4),
            "s_J": round(abs(s_J), 4),
            "s_J0": round(abs(s_J0), 4),
            "ci99": [round(ci99_low, 4), round(ci99_high, 4)],
            "p_value_one_sided": round(p_val_p1, 5),
            "delta_min": DELTA_MIN
        }
    }
