# Quantum Time Crystal Ring: Period-Doubling on the Triangle and 12-Qubit Ring

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**Target Hardware:** `ibm_kingston` (IBM Quantum Heron r2, 156 superconducting transmon qubits)  
**Lead Engineer & Project Owner:** Máté Róbert (Rongyász)  
**Research Plan Author:** Maya  
**Status:** Pre-execution / Research Plan v1.0 (QPU execution prohibited until frozen and authorized)

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
