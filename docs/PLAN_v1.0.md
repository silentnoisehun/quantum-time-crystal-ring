# Discrete Time Crystal (DTC) Research Plan: Period Doubling on the Triangle and 12-Qubit Ring

**Document ID:** `PLAN_v1.0`  
**Date:** 2026-11-18, 17:34 UTC (18:34 Budapest)  
**Author:** Maya, on request of Lead Engineer & Project Owner Máté Róbert (Rongyász)  
**Status:** v0.1 Draft Research Plan (NOT a frozen preregistration yet; QPU execution is NOT permitted)  
**Hardware Target:** Exclusively `ibm_marrakesh` (IBM Quantum Heron r2, 156 qubits, per authorized deviation DEV-001 by Máté Róbert). If `ibm_marrakesh` is unavailable, execution is cancelled.

---

## 1. Research Question and Non-Claims

A discrete time crystal (DTC) is a periodically driven many-body system whose local observables oscillate at twice the driving period (period-doubling subharmonic response, $2T$-periodicity), robust against driving pulse imperfections ($\varepsilon \ne 0$).

This work investigates Máté's core geometric and physical intuitions:
1. **The rotating triangle ring with a quiet center:** A closed boundary-free loop where every site has coordination number $z=2$.
2. **Active support:** Periodic Floquet drive kicking the system back into state rotation.
3. **The elastic triangle lesson:** In a mechanical rotating elastic triangle, fatigue of individual bands determines the stopping configuration. To prevent QPU hardware inhomogeneity from dictating the outcome, a strict **"band-replacement" (gumicsere) control** is instituted (permuting logical-to-physical qubit assignments).

### Scope and Open Device-Level Question
On the specific `ibm_kingston` Heron processor, on a 3-qubit triangle (synthetic loop via SWAP) and a 12-qubit native heavy-hex ring:
- Over how many Floquet cycles ($t=0\dots T$), across what pulse errors ($\varepsilon$), and under what disorder ($W$) does period-doubling survive?
- How does the interacting loop ($J \ne 0$) contrast with the non-interacting control ($J = 0$, matched idle duration) and with ideal/noisy simulations?
- How much of site-dependent decay is explained by physical qubit defects versus Floquet dynamics?

### Explicit Non-Claims
- **No new physics:** DTCs are theoretically and experimentally established.
- **Finite-size limitation:** 12 qubits measured over finite cycles do not constitute a thermodynamic many-body phase transition. The paper title is strictly *"Lifetime and $\varepsilon$-Tolerance of Period Doubling on Heavy-Hex Geometries"*, not *"Observation of a Time Crystal Phase"*.
- **3-Qubit triangle is a few-body toy test:** It serves as a geometric benchmark, not a many-body phase.
- **No memory / spatial persistence claims:** This protocol tests driven Floquet dynamics, not quantum memory or substrate persistence.

---

## 2. Literature Baseline

1. **Theory:**
   - *Khemani et al.*, Phys. Rev. Lett. 116, 250401 (2016) [arXiv:1508.03344]: Phase structure of driven systems; MBL-DTC in Floquet Ising spin chains.
   - *Else, Bauer, Nayak*, Phys. Rev. Lett. 117, 090402 (2016) [arXiv:1603.08001]: Spontaneous discrete time translation symmetry breaking in driven MBL systems.
2. **Key Experiments:**
   - *Mi et al. (Google)*, Nature 601, 531 (2022) [arXiv:2107.13571]: Eigenstate-ordered DTC on superconducting qubits. We adopt their time-reversal echo protocol (separating external decoherence from internal thermalization) and testing diverse initial computational bitstrings.
   - *Frey & Rachel*, Sci. Adv. 8, eabm7652 (2022) [arXiv:2105.06632]: 57-qubit chain DTC; disorder ($W \ne 0$) vs clean ($W = 0$) baseline.
   - *Randall et al.*, Science 374, 1474 (2021) [arXiv:2107.00736]: Diamond $^{13}\text{C}$ nuclear spin simulator.
   - *Shinjo, Seki, Yunoki*, arXiv:2510.13577 (2026): Noise-stabilized DTC on IBM Eagle and Heron processors on Kagome lattice with ancilla routing. Demonstrates that device noise can itself mimic long-lived subharmonic DTC signatures. This mandates our strict $J = 0$ duration-matched, echo, and gumicsere controls.

---

## 3. Geometry and Graph Fidelity

### 3.1 Heavy-Hex Topology
- The IBM Heron heavy-hex lattice contains **no native 3-cycles** (girth $\ge 6$, smallest loops are 12-qubit hexagons).
- **Triangle realization ($C_3$):** 3-qubit path $a-b-c$ with native links $a-b$ and $b-c$. The $a-c$ edge requires SWAP routing:
  1. *Round-trip SWAP per cycle:* SWAP$(b,c)$, $ZZ(a,b)$, SWAP$(b,c)$.
  2. *Tracked permutation:* Retain SWAP, tracking logical-to-physical qubit mapping dynamically.
  3. *Merged SWAP+ZZ unitary.*
  All three variants will be transpiled on live `ibm_kingston`, evaluating CZ count and schedule duration against the 2-edge path control.
- **12-Qubit Hexagon Ring ($C_{12}$):** Native closed loop where every site has coordination number 2. No SWAP required.
- **Algorithmic Ring Selection:** Pre-registered scoring rule (edge CZ error + qubit readout error) selects the optimal 12-qubit hexagon on execution day. Ad-hoc exploration of multiple rings on QPU is forbidden (anti-F2).

### 3.2 Graph Fidelity Verification
- Graph extraction test verifying $C_3$ (3 vertices, 3 edges, regular degree 2) and $C_{12}$ (12 vertices, 12 edges, regular degree 2).
- Mandatory negative test rejecting non-target topologies (e.g. star graphs).
- Unitary fidelity test: transpiled physical cycle mapped back to logical frame must equal ideal cycle with fidelity $F = 1.0$ within numerical tolerance.
- ASCII/visual layout diagram approved by Máté before execution.

---

## 4. Floquet Circuit and Observables

### 4.1 Floquet Cycle Unitary
Each Floquet cycle $U_F$ consists of three successive layers separated by barriers:
1. **Pulse Layer:** $R_X(\pi(1-\varepsilon))$ on all qubits. $\varepsilon = 0$ is an exact $\pi$-flip; $\varepsilon > 0$ introduces controlled rotational deviation.
2. **Interaction Layer:** $R_{ZZ}(\phi_{ij})$ on all active graph edges. Nominal coupling $\phi_{ij} = J$.
3. **Disorder Layer:** $R_Z(h_i)$ on all qubits, with site fields $h_i \in [-W, W]$ sampled uniformly from a fixed pseudo-random seed.

### 4.2 Observables (Calculated from Raw Counts)
- Normalized Magnetization: $m(t) = \frac{1}{L} \sum_{i=1}^L z_i(0) \langle Z_i(t) \rangle$, where $z_i(0) \in \{+1, -1\}$.
- Primary Test Statistic: $S(t) = \frac{1}{2} [m(t) - m(t+1)]$. Directly quantifies subharmonic oscillation amplitude without curve fitting.
- Subharmonic Spectral Peak: Discrete Fourier Transform of $m(t)$, tracking peak height and frequency offset from $f = 1/2$.
- Envelope Decay Lifetime $\tau$ (Secondary): Exponential fit on $|S(t)|$ with bootstrap confidence intervals.
- Site-Resolved Magnetization: $d_i(t) = \frac{1}{2} z_i(0) [\langle Z_i(t) \rangle - \langle Z_i(t+1) \rangle]$ for band-replacement analysis.
- Echo-Normalized Signal: $E(t) = |\langle \psi_0 | U_F^{-t} U_F^t | \psi_0 \rangle|^2$, reporting $S(t) / \sqrt{E(t)}$ to decouple external decoherence.

---

## 5. Control Matrix

| Control Branch | Scientific Purpose | Theoretical Standard Expectation |
| :--- | :--- | :--- |
| **$J = 0$ (Duration-Matched)** | Is interaction necessary? | Beats at frequency $\varepsilon$; period-doubling collapses with $\varepsilon$. |
| **$W = 0$** | Is disorder necessary? | Prethermal DTC response vs MBL localization on finite system. |
| **$\varepsilon$-Sweep ($J$ vs $J=0$)** | Robustness against pulse error | Finite plateau around $\varepsilon=0$ for $J \ne 0$; linear decay for $J=0$. |
| **DD On vs Off** | Impact of idle spectator noise | Assesses whether dynamical decoupling alters primary contrast. |
| **Gumicsere (Permutation)** | Hardware defect vs Floquet dynamics | Physical qubit variance vs logical disorder variance across rotated layouts. |
| **Time-Reversal Echo** | Pure decoherence floor | $E(t)$ decays from device $T_1/T_2$; intrinsic dynamics invariant. |
| **Intra-Job Temporal Drift** | Within-job calibration drift | Repeat baseline circuits at start, middle, and end of batch job. |
| **Interleaved Randomization** | Sequence ordering artifact guard | Random shuffle of all circuits using a transparent fixed seed. |
| **In-Situ Readout Calibration**| Actual measurement fidelity | Ground $|00\dots0\rangle$, $|11\dots1\rangle$ and 2 random bitstrings in the same job. |
| **Triangle Path Control ($a-b-c$)**| Effect of closing the loop | Path without $a-c$ edge contrasts loop topology against linear chain. |

---

## 6. Circuit Budget and QPU Constraints

- Single unified batch job on `ibm_kingston`.
- Estimated total circuits: $\sim 70-85$ circuits for $T=12$.
- Shots per circuit: determined by power analysis from noisy Aer simulation.
- Execution time guard: QPU runtime estimate must be $\le 60\text{ s}$ unless explicitly approved by Máté.

---

## 7. Hypotheses, Decision Rules, and Statistics

### 7.1 Primary Hypotheses (Family-wise $\alpha = 0.01$, Holm-Bonferroni)
1. **$P_1$ (Interaction protects period doubling):** $S_J(t^*) - S_{J=0}(t^*) > 0$ on the 12-qubit ring at $\varepsilon_0$. One-sided.
2. **$P_2$ (Gumicsere / Hardware Inhomogeneity):** Variance of site signal $d_i(t^*)$ explained by physical qubit index versus logical disorder site $h_i$. Permutation test with fixed seed. Two-sided: `PHYSICAL QUBIT GOVERNS` / `LOGICAL SITE GOVERNS` / `INCONCLUSIVE`.
3. **$P_3$ ($\varepsilon$-Tolerance Width):** $\varepsilon_\text{half}(J) > \varepsilon_\text{half}(J=0)$, where $\varepsilon_\text{half}$ is the error where $S(t^*)$ drops below half its $\varepsilon=0$ amplitude. One-sided bootstrap.

### 7.2 Decision Categories
- **SUPPORTED:** Holm-adjusted $p < 0.01$ and $99\%$ CI strictly on predicted side.
- **NULL:** Interval contains 0 and upper bound is below minimum detectable effect $\delta_\text{min}$.
- **INCONCLUSIVE:** Interval contains 0 and exceeds $\delta_\text{min}$.
- **INVALID:** Predefined validity guard violated (readout error above threshold, missing shots, gate count mismatch).
- **ANALYSIS_ERROR:** Software crash or code exception (distinct from physical nulls).

---

## 8. QIA Anti-Defect Checklist (Targeting Flawless Reproducibility)

- **Anti-F1 (Self-built reference):** Primary contrast is intra-job between $J \ne 0$ and duration-matched $J = 0$. Aer simulation is explicitly labelled as an F1 reference.
- **Anti-F2 (Cherry-picking):** Primary test evaluates fixed pre-registered cycle $t^*$. Algorithmic ring selection rule frozen in advance.
- **Anti-F3 (Widthless claim):** Every statistic accompanied by 99% bootstrap / Wilson interval.
- **Anti-F4 (Unreleased data):** Complete raw bitstrings, calibration snapshots, target schemas, transpiled QASM3/QPY, and random seeds published to Zenodo.
- **Anti-F5 (Discrepant recalculation):** Single `recount.py` regenerates every number and table directly from raw JSON counts.
- **Anti-F6 (Text-table mismatch):** Text and tables programmatically verified. No overreaching terminology ("memory", "time crystal phase", "proven").
- **Anti-F7 (Classical superiority acknowledged):** Paper explicitly notes that 12-qubit ideal dynamics are efficiently simulable classically; device-level characterization of superconducting hardware is the sole objective.

---

## 9. Phased Execution Gates

```
[PLAN_v1.0] -> [Step 1: Geometry & Fidelity] -> Gate: Máté approves diagram
            -> [Step 2: Ideal Simulation & Theory Prediction]
            -> [Step 3: Noisy Aer Simulation & Power Analysis]
            -> [Step 4: Analyzer Null-Test & Sensitivity] -> Gate: Null-test valid, power >= 80%
            -> [Step 5: Preregistration Freeze & Hashing] -> Gate: Frozen commit hash
            -> [Step 6: Independent Audit (Maya)] -> Gate: Máté approves submission
            -> [Step 7: QPU Run on ibm_kingston]
            -> [Step 8: Frozen Analysis & Recount]
```
