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
