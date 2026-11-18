# Pre-Measurement Predictions: 3-Column Protocol

**Repository:** `quantum-time-crystal-ring`  
**Target:** `ibm_kingston` (156Q Heron r2)  
**Rule:** All three columns must be frozen, committed, and hashed prior to QPU job creation.

| Observable / Question | 1. Máté's Prediction (Lead Engineer) | 2. Textbook Quantum Mechanics (Ideal Simulation) | 3. Noisy Aer Model (Live Kingston Snapshot, F1 Reference) |
| :--- | :--- | :--- | :--- |
| **$P_1$: Interaction Protection** ($S_J(t^*) - S_{J=0}(t^*)$ at $\varepsilon_0$) | *[To be filled by Máté before freeze]* | **+0.8074** ($S_J = 0.9291$, $S_{J=0} = 0.1217$) | **+0.6605** ($S_J = 0.7962$, $S_{J=0} = 0.1357$), 99% CI: [0.6441, 0.6770] |
| **$P_2$: Gumicsere (Permutation)** (Physical Qubit vs Logical Disorder Site) | *[To be filled by Máté before freeze]* | **Logical disorder site governs** (noiseless layout has zero physical defect) | **Physical qubit defects compete** (device noise adds site-dependent readout/CZ variation) |
| **$P_3$: $\varepsilon$-Tolerance Width** ($\varepsilon_\text{half}(J) - \varepsilon_\text{half}(J=0)$) | *[To be filled by Máté before freeze]* | **+0.1305** ($\varepsilon_\text{half}(J)=0.200$, $\varepsilon_\text{half}(J=0)=0.070$) | **+0.0820** (decayed by device decoherence) |
| **Beat Frequency of $J=0$ Branch** | *[To be filled by Máté before freeze]* | **$\Delta f = \varepsilon_0 = 0.1000$** (spectral peak at $f = 0.4706$) | **$\Delta f \approx 0.1000$** |
| **Disorder Effect** ($S_{W \ne 0}(t^*) - S_{W=0}(t^*)$) | *[To be filled by Máté before freeze]* | **+0.0397** ($S_W = 0.9291$, $S_{W=0} = 0.8894$) | **+0.0377** |
| **Triangle vs Open Path** ($S_\text{triangle}(t^*) - S_\text{path}(t^*)$) | *[To be filled by Máté before freeze]* | **-0.6565** ($S_\text{tri} = 0.0827$, $S_\text{path} = 0.7392$) | **-0.3800** |
| **Decoherence Floor** ($E(t^*)$ echo survival) | *[To be filled by Máté before freeze]* | **1.0000** (noiseless) | **0.7634** (bulk $T_1/T_2$ decay) |

---

### Máté's General Scientific Notes & Expectations
*(Space reserved for Máté Róbert's personal scientific hypothesis and reflections prior to freezing)*
