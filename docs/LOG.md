# Engineering & Scientific Audit Log — Quantum Time Crystal Ring

All timestamps recorded in UTC and Budapest local time. Every step is an atomic gate.

---

### [2026-11-18 17:34 UTC | 18:34 Budapest]
- **Event:** Research Plan v0.1 draft received from Maya, requested by Lead Engineer Máté Róbert.
- **Repository Initialized:** `E:\Silent Coder\quantum-time-crystal-ring`
- **Scope:** Discrete Time Crystal (DTC) period-doubling dynamics on `ibm_kingston` (Heron r2, 156Q) comparing a 3-qubit synthetic triangle and a 12-qubit native heavy-hex ring.
- **Status:** Planning phase. QPU execution disabled.

---

### [2026-11-18 17:45 UTC | 18:45 Budapest]
- **Event:** Repository skeleton established with directory schema (`docs/`, `prereg/`, `src/`, `sim/`, `data/`, `results/`, `tests/`).
- **Research Plan:** Generated `docs/PLAN_v1.0.md` detailing all 8 execution gates, QIA anti-defect protocols (anti-F1 through anti-F7), and 3 primary pre-registered hypotheses.

---

### [2026-11-18 17:46 UTC | 18:46 Budapest]
- **Target Backend Decision:** Máté explicitly authorized execution on `ibm_marrakesh` (`"a maracashen fussin"`).
- **Deviation DEV-001 Logged:** Replaced planned single-backend restriction (`ibm_kingston`) with `ibm_marrakesh`.
- **Backend Status:** Connected to `ibm_marrakesh` (156 qubits, Heron r2, operational=True, pending_jobs=0).

---

### [2026-11-18 17:50 UTC | 18:50 Budapest]
- **Gate 1 Closed:** Máté approved the geometry layout, physical qubit allocations (`[131, 132, 133, 134, 135, 139, 155, 154, 153, 152, 151, 138]` for $C_{12}$, `[151, 138, 131]` for $C_3$), and topology diagram.
- **Next Gate Opened:** Step 2 — Ideal Simulation & Parameter Sweep (`sim/ideal/`).

---

### [2026-11-18 18:00 UTC | 19:00 Budapest]
- **Gate 2 Closed:** Ideal classical statevector simulation completed (`sim/ideal/ideal_predictions.json`). Optimal parameters frozen: $J=0.4$, $W=1.5$, $\varepsilon_0=0.10$, $t^*=6$, $T=16$.
- **Gate 3 Closed:** Noisy Aer simulation on `ibm_marrakesh` device model completed (`sim/noisy/noisy_aer_predictions.json`). Calibration snapshot frozen (`data/frozen/marrakesh_calibration_snapshot_20261118.json`).
- **Predictions Updated:** Standard Physics and Noisy Aer columns populated in `docs/PREDICTIONS.md`.

---

### [2026-11-18 18:18 UTC | 19:18 Budapest]
- **Gate 4 Closed:** Master analyzer validated (`src/validate_analyzer.py`). Null-test ($N=1000$): Type I error = 0.0000, error rate = 0.0000. Power at $\delta_\text{min}=0.05$ ($N=300$): 100.0%.
- **Gate 5 Closed:** Master circuit table (85 circuits), parameter card, and SHA256 hash card frozen in `prereg/`. Master commit ready.

---

### [2026-11-18 18:20 UTC | 19:20 Budapest]
- **Gate 6 Closed:** Máté registered his personal hypothesis in `docs/PREDICTIONS.md` Column 1 (*"A perem nélküli zárt 12-es gyűrű geometriai védelmet nyújt, így a periódus-kettőződés élettartama meghaladja a zajos Aer becslést"*).
- **Gate 7 Authorized:** Máté formally authorized single-job QPU dispatch to `ibm_marrakesh` (85 circuits, 2048 shots).

---

### [2026-11-18 18:22 UTC | 19:22 Budapest]
- **Gate 7 Execution:** Unified batch job submitted and executed on `ibm_marrakesh` (Heron r2, 156Q).
- **Job ID:** `dbuupiv82tmc73du4u70`
- **Circuits Executed:** 85 circuits $\times$ 2048 shots, randomized via deterministic shuffle seed `20261119`.
- **Runtime:** Completed in ~7.8 seconds on physical QPU.
- **Data Persistence:** Raw counts saved to `data/raw/raw_counts_dbuupiv82tmc73du4u70.json`; dispatch metadata saved to `data/raw/submission_record_dbuupiv82tmc73du4u70.json`.

---

### [2026-11-18 18:28 UTC | 19:28 Budapest]
- **Gate 8 Analysis:** Frozen master analyzer (`src/analyzer.py`, SHA256 frozen in Gate 5) executed without modification via `src/run_analysis_qpu.py`.
- **Primary Hypothesis P1:** `SUPPORTED`
  - Contrast at $t^*=6$: $\Delta S(6) = +0.5527$ [99% CI: 0.5385, 0.5671], $p < 10^{-5}$.
  - Point difference strictly exceeds $\delta_\text{min} = 0.05$.
- **Hypothesis P2 (Gumicsere):** Confirmed high topological homogeneity across cyclic disorder permutations ($\text{Var} = 0.000076$).
- **Hypothesis P3 ($\varepsilon$-Tolerance Plató):** Confirmed stable subharmonic order up to $\varepsilon = 0.10$ ($S_J = 0.6690$) vs collapse of non-interacting control ($S_{J=0} = 0.1163$).
- **Column 1 Comparison:** Experimental contrast (+0.5527) is positive, but lower than noisy Aer (+0.6605) due to physical gate noise and crosstalk on Heron r2.
- **Gate 8 Closed:** Analysis and summary artifacts committed. Project execution complete.
