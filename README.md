# Quantum Time Crystal Ring: Period-Doubling on the Triangle and 12-Qubit Ring

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**Target Hardware:** `ibm_marrakesh` (IBM Quantum Heron r2, 156 superconducting transmon qubits; authorized deviation DEV-001)  
**Lead Engineer & Project Owner:** Máté Róbert (Rongyász)  
**Research Plan Author:** Maya  
**Status:** Gate 8 Complete — Executed on QPU (`dbuupiv82tmc73du4u70`) & Evaluated with Frozen Analyzer  

---

## Key Experimental Results (Gate 8 Summary)

The pre-registered master analyzer was executed on the raw count data from IBM Marrakesh without modification:

- **Primary Hypothesis P1 (Interaction Protection):** **SUPPORTED**
  - **$\Delta S(6) = |S_J(6)| - |S_{J=0}(6)| = +0.5527$**
  - **99% Bootstrap CI:** `[0.5385, 0.5671]`, strictly exceeding pre-registered threshold $\delta_\text{min} = 0.05$.
  - **One-Sided p-value:** $p < 10^{-5}$ ($0.0$).
- **Hypothesis P2 (Gumicsere / Inhomogeneity Test):** **RING HOMOGENEITY CONFIRMED**
  - Subharmonic order parameter variance across 4 cyclic disorder shifts on the physical ring: $\text{Var}(S) = 0.000076$ ($\sigma = 0.0087$).
  - Confirms that the closed boundary-free 12-qubit ring topology averages out physical qubit irregularities.
- **Hypothesis P3 ($\varepsilon$-Tolerance Plató):** **CONFIRMED**
  - The interacting system maintains high subharmonic order across perturbations ($S_J(\varepsilon=0.10) = 0.6690$), whereas the non-interacting system collapses rapidly ($S_{J=0}(\varepsilon=0.10) = 0.1163$) and undergoes phase-inversion beats.
- **Hypothesis Evaluation (Máté's Prediction vs Hardware):**
  - Máté hypothesized that boundary-free ring geometry would yield contrast exceeding the noisy Aer simulation ($> +0.66$).
  - Measured QPU contrast is $+0.5527$. The positive DTC stabilization is confirmed, but lower than Aer noisy (+0.6605) due to real device CZ gate infidelities and spectator crosstalk on Heron r2, in strict accordance with textbook open quantum systems physics.

For full trajectories, tables, and plots, see [`results/RESULTS_SUMMARY.md`](file:///E:/Silent%20Coder/quantum-time-crystal-ring/results/RESULTS_SUMMARY.md).

---

## Abstract

This repository investigates the lifetime and $\varepsilon$-tolerance of period-doubling subharmonic oscillations (discrete time crystalline signatures) in periodically driven Floquet spin systems on an IBM Heron superconducting quantum processor (`ibm_kingston`). 

We implement two distinct closed geometries:
1. A **3-qubit triangle ($C_3$)**, realizing periodic boundary conditions via active SWAP routing over a linear transmon chain.
2. A **12-qubit hexagon ring ($C_{12}$)**, leveraging the native boundary-free hexagonal loop topology of the heavy-hex lattice with zero SWAP overhead.

The protocol evaluates the persistence of period doubling under intentional pulse perturbation $\varepsilon$, disorder $W$, and interaction $J$, contrasted directly against:
- Duration-matched non-interacting controls ($J = 0$ with idle wait times matching active gate durations).
- "Gumicsere" (band replacement) rotational permutations isolating physical qubit defects from genuine Floquet dynamics.
- Time-reversal echoes ($U_F^{-t} U_F^t$) isolating bulk environmental decoherence.

All evaluations are conducted according to strict pre-registration standards, with automated graph fidelity verification, count-level statistics, and QIA anti-defect protocols.

---

## Repository Structure

```
quantum-time-crystal-ring/
├── docs/
│   ├── PLAN_v1.0.md           # Master research plan and execution protocols
│   ├── PREDICTIONS.md         # 3-column pre-registered predictions (Máté / Theory / Aer)
│   ├── DEVIATIONS.md          # Formal timestamped deviations log
│   ├── ERRATA.md              # Historical errata log
│   └── LOG.md                 # Scientific and engineering progress log
├── prereg/                    # Frozen circuit tables, parameter cards, SHA256 hashes
├── src/                       # Circuit compilers, topology checkers, analyzers, submission guard
├── sim/
│   ├── ideal/                 # Unitary Schrödinger / statevector simulations
│   └── noisy/                 # Device-calibrated Aer simulations (F1 reference)
├── data/
│   ├── raw/                   # Raw bitstring counts from QPU (immutable post-write)
│   └── frozen/                # Transpiled QPY/QASM3 and calibration snapshots
├── results/                   # Recomputed tables, publication figures
└── tests/                     # Graph fidelity, negative tests, null-tests, recount checkers
```

---

## Core Rules & Verification Protocols

1. **Gate Sequence Integrity:** Every step must pass its defined gate before proceeding.
2. **Device Dedication:** Exclusively executed on `ibm_kingston`. Fallback backends are strictly prohibited.
3. **Graph Fidelity:** Circuits are tested for exact topology ($C_3$ and $C_{12}$) with mandatory negative controls rejecting non-target topologies.
4. **Count-Level Statistics:** All metrics ($m(t)$, $S(t)$, $\chi^2$, Wilson score intervals, and bootstrap errors) are derived directly from integer bitstring counts.
5. **No Ad-Hoc Tuning:** Parameters, seeds, and QPU layouts are selected algorithmically and frozen prior to job submission.
