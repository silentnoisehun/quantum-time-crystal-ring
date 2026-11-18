# Gate 8: Experimental Results Summary — IBM Marrakesh

**Date & Time:** 2026-11-18 18:25 UTC | 19:25 Budapest  
**Backend:** `ibm_marrakesh` (Heron r2, 156 superconducting qubits; authorized deviation DEV-001)  
**Job ID:** `dbuupiv82tmc73du4u70`  
**Total Circuits Executed:** 85 circuits $\times$ 2048 shots (unified single batch)  
**Execution Runtime:** ~7.8 seconds on QPU  
**Raw Data:** [`data/raw/raw_counts_dbuupiv82tmc73du4u70.json`](../data/raw/raw_counts_dbuupiv82tmc73du4u70.json)  
**Submission Record:** [`data/raw/submission_record_dbuupiv82tmc73du4u70.json`](../data/raw/submission_record_dbuupiv82tmc73du4u70.json)  
**Full Machine Report:** [`results/qpu_analysis_report.json`](qpu_analysis_report.json)  

---

## 1. Executive Summary & Verdicts

| Pre-Registered Observable | Frozen Criterion | Hardware Outcome | Verdict |
| :--- | :--- | :--- | :--- |
| **$P_1$: Interaction Protection (DTC Order)** | $\Delta S(t^*) = \|S_J(6)\| - \|S_{J=0}(6)\| > 0.05$, $p < 0.0033$, CI99 low $> 0$ | **$\Delta S(6) = +0.5527$** [99% CI: **0.5385, 0.5671**], $p < 10^{-5}$ | **SUPPORTED (Tankönyvi QM teljesült; Máté jóslata nem)** |
| **$P_2$: Gumicsere (Inhomogeneity Test)** | Comparison of order across cyclic disorder shifts $\sigma \in \{0, 3, 6, 9\}$ | $S \in [0.6448, 0.6690]$, $\text{Var} = 0.000076$ ($\sigma = 0.0087$) | **A zavar helye nem számított a gyűrűn, de kontroll és küszöb híján a peremtelen védelem nem állítható** |
| **$P_3$: $\varepsilon$-Tolerance Plateau** | Plateau in $S_J(\varepsilon)$ vs collapse in $S_{J=0}(\varepsilon)$ | $S_J(\varepsilon=0.10) = 0.6690$ vs $S_{J=0}(\varepsilon=0.10) = 0.1163$ | **Plató megfigyelve** |

---

## 2. Three-Column Prediction vs Hardware Measurement

Comparison of the pre-registered predictions against the live physical measurements from `ibm_marrakesh`:

| Observable / Question | 1. Máté's Prediction (Lead Engineer) | 2. Textbook QM (Ideal Simulation) | 3. Noisy Aer Model (Marrakesh Snapshot) | 4. Hardware Actual (`ibm_marrakesh`) | Hardware Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **$P_1$: Interaction Contrast $\Delta S(6)$** | Exceeds Noisy Aer ($> +0.66$) via topological protection | **+0.8074** | **+0.6605** [0.6441, 0.6770] | **+0.5527** [0.5385, 0.5671] | **Máté jóslata: nem teljesült.** (Mért +0.5527 elmarad az Aer +0.6605-től). A tankönyvi DTC védelem teljesült ($\Delta S > 0$), de az extra geometriai védelem elbukott. |
| **$P_2$: Gumicsere (Disorder Invariance)** | Boundary-free ring protects against localized defects | Logical disorder governs ($\text{Var}=0$) | Device noise adds site variation | **$\text{Var} = 0.000076$** ($\Delta S_\text{max} \le 0.0242$) | **A zavar helye nem számított a gyűrűn**, de nyitott 12-es lánc kontroll és előre rögzített küszöb nélkül ebből nem következik, hogy a peremtelen gyűrű véd. |
| **$P_3$: $\varepsilon$-Tolerance Plató** | Robust subharmonic plateau | High plateau ($\varepsilon_\text{half}=0.20$) | Decayed plateau ($\Delta \varepsilon_\text{half}=0.082$) | **$S_J(0.10) = 0.6690$**, $S_{J=0} = 0.1163$ | **Plató megfigyelve:** $J=0$ összeomlik, a hajtott $J=0.4$ stabil marad. |
| **Beat Frequency of $J=0$** | $\Delta f = \varepsilon_0 = 0.10$ | $\Delta f = 0.10$ | $\Delta f \approx 0.10$ | **Phase inversion at $t=8$** ($S_{J=0} = -0.1852$) | **Tankönyvi QM igazolva** |
| **Triangle Module ($N=3$)** | A zárt él aktív dinamikát tart fenn | **-0.6565** ($S_\text{tri} = 0.0827$, $S_\text{path} = 0.7392$) | **-0.3800** | **$S_\text{tri} = +0.1917$, $S_\text{path} = +0.6673$** | **Máté jóslata nem teljesült.** A zárt háromszög elnyomott (54 CZ a SWAP-ok miatt vs 24 CZ az úton). Kapuszám-illesztés nélkül a kapuzaj és a frusztráció hatása összeolvad. |
| **Intra-Job Drift ($t=6$, 4 reps)** | Stable run | Stable | Stable | **$\sigma_\text{drift} = 0.0081$** ($m \in [0.6696, 0.6912]$) | **Stabil kalibráció (< 1% szórás)** |

> [!IMPORTANT]
> **A Jóslat Becsületes Értékelése:**  
> Máté előregisztrált felfedező hipotézise az volt, hogy a perem nélküli 12-es gyűrű olyan topológiai/geometriai védelmet nyújt, ami miatt a periódus-kettőződés élettartama meghaladja a zajos Aer szimuláció jóslatát ($\Delta S > +0.66$).  
> **Ez a jóslat elbukott.** A fizikai QPU-n mért kontraszt $+0.5527$ [99% CI: 0.5385, 0.5671], ami szignifikánsan alacsonyabb az Aer szimuláció által jósolt $+0.6605$-nél. A tankönyvi kvantummechanika által megkövetelt diszkrét időkristály-védelem valóságosan megjelent ($p < 10^{-5}$ a nem kölcsönható kontrollhoz képest), de azt a fizikai transmonok kapuhulladéka és a nézőpont-qubitek fáziszaja korlátozta, semmilyen „extra geometriai csoda” nem lépett fel.

---

## 3. Full Time Evolution Trajectories ($t = 0 \dots 16$)

### Staggered Magnetization $m(t)$ and Order Parameter $S(t) = \frac{1}{2}(m(t) - m(t+1))$

| Cycle $t$ | $m_J(t)$ (Interacting) | $m_{J=0}(t)$ (No Interactions) | $S_J(t)$ | $S_{J=0}(t)$ | Contrast $\Delta S(t)$ |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **0** | +0.9619 | +0.9618 | +0.9194 | +0.9394 | -0.0200 |
| **1** | -0.8768 | -0.9170 | -0.8450 | -0.8851 | -0.0401 |
| **2** | +0.8132 | +0.8533 | +0.8058 | +0.7846 | +0.0212 |
| **3** | -0.7984 | -0.7159 | -0.7885 | -0.6442 | +0.1443 |
| **4** | +0.7786 | +0.5725 | +0.7533 | +0.4756 | +0.2777 |
| **5** | -0.7279 | -0.3787 | -0.7043 | -0.2913 | +0.4130 |
| **6 ($t^*$)** | **+0.6807** | **+0.2040** | **+0.6690** | **+0.1163** | **+0.5527** |
| **7** | -0.6574 | -0.0286 | -0.6305 | +0.0435 | +0.5870 |
| **8** | +0.6037 | -0.1156 | +0.5930 | -0.1852 | +0.4078 |
| **9** | -0.5824 | +0.2548 | -0.5566 | +0.3011 | +0.2555 |
| **10** | +0.5309 | -0.3475 | +0.5220 | -0.3788 | +0.1432 |
| **11** | -0.5130 | +0.4101 | -0.4982 | +0.4056 | +0.0926 |
| **12** | +0.4833 | -0.4012 | +0.4727 | -0.3894 | +0.0833 |
| **13** | -0.4620 | +0.3776 | -0.4432 | +0.3457 | +0.0975 |
| **14** | +0.4243 | -0.3137 | +0.4123 | -0.2714 | +0.1409 |
| **15** | -0.4002 | +0.2290 | -0.3847 | +0.1577 | +0.2270 |
| **16** | +0.3691 | -0.0864 | — | — | — |

---

## 4. Perturbation Tolerance Sweep ($\varepsilon \in [0.00 \dots 0.20]$)

| Perturbation $\varepsilon$ | $S_J(6)$ (DTC) | $S_{J=0}(6)$ (Trivial) | Contrast $\Delta S = \|S_J\| - \|S_{J=0}\|$ | Physical State |
| :---: | :---: | :---: | :---: | :--- |
| **0.00** | +0.7379 | +0.9522 | -0.2143 | Tiszta $\pi$-pulzus határeset (triviális forgás) |
| **0.03** | +0.7339 | +0.8431 | -0.1093 | Kis szöghiba |
| **0.06** | +0.7122 | +0.5883 | +0.1239 | Átmenet a DTC védelem tartományába |
| **0.10** | **+0.6690** | **+0.1163** | **+0.5527** | **Optimális munkapont (maximális kontraszt)** |
| **0.15** | +0.5628 | -0.3274 | +0.2354 | Nagy perturbáció: $J=0$ fázist fordított |
| **0.20** | +0.4362 | -0.3479 | +0.0883 | Erős perturbáció: a DTC rend lecsökken |

---

## 5. Geometriai Inhomogenitás ("Gumicsere") Vizsgálata

A kvázi-rendezetlenségi $h_i \in [-W, W]$ mintázat ciklikus eltolása $\sigma \in \{0, 3, 6, 9\}$ a fizikai gyűrűn:
- Elforgatás 0: $S = 0.6690$
- Elforgatás +3: $S = 0.6448$
- Elforgatás +6: $S = 0.6594$
- Elforgatás +9: $S = 0.6607$

**Szórás:** $\text{Var}(S) = 0.000076$ ($\sigma = 0.0087$)  
**Összevetés:** A futáson belüli 4 azonos replika szórása $\sigma_\text{drift} = 0.0081$. A zavar pozíciójának variálása nem okozott a driftnél nagyobb eltérést.  
**Kritikai korlát:** Nyitott 12-es lánc kontroll és előre definiált kvantitatív küszöb hiányában ebből nem következtethető ki, hogy a peremtelen topológia nyújt védelmet.

---

## 6. Háromszög Modul ($N=3$) és a Kapuzaj Kérdése

$t^* = 6$-nál:
- **12-Qubites Bipartit Gyűrű ($C_{12}$):** $S = +0.6690$
- **3-Qubites Nyílt Út ($P_3$):** $S = +0.6673$ (24 CZ kapu a 6 ciklus alatt)
- **3-Qubites Zárt Háromszög ($C_3$):** $S = +0.1917$ (54 CZ kapu a transmon SWAP-ok miatt)

**Fizikai Magyarázat:**  
Máté jóslata (a zárt él aktív dinamikát tart fenn) nem teljesült; a zárt háromszög erősen elnyomott. Bár a páratlan ciklus geometriai frusztrációt okoz a Néel-állapotban (`010`), a hardveres megvalósításban az aktív SWAP routing miatt **54 CZ kapu** futott, míg a nyitott útnál csak **24 CZ kapu**. Kapuszámra illesztett kontroll hiányában a kapudekoherencia és a geometriai frusztráció hatása összeolvad, nem választható szét.

---

## 7. Nyers Adatok Sorrendje & Determinisztikus Visszafejtés (Shuffle Inversion)

A hardveres szisztematikus drift és időbeli torzítás elkerülése érdekében az 85 áramkör **determinisztikusan keverve** (seed: `20261119`) futott a QPU-n.

A [`data/raw/raw_counts_dbuupiv82tmc73du4u70.json`](../data/raw/raw_counts_dbuupiv82tmc73du4u70.json) fájlban a mérési eredmények a lefutott sorrendben találhatók. Az eredeti áramkörökhöz való hozzárendeléshez a [`data/raw/submission_record_dbuupiv82tmc73du4u70.json`](../data/raw/submission_record_dbuupiv82tmc73du4u70.json) fájlban tárolt `execution_order` tömböt kell használni:

```python
import json

# 1. Betöltés
with open("prereg/circuit_table.json") as f:
    table = json.load(f)["circuits"]
with open("data/raw/submission_record_dbuupiv82tmc73du4u70.json") as f:
    order = json.load(f)["execution_order"]
with open("data/raw/raw_counts_dbuupiv82tmc73du4u70.json") as f:
    raw_counts = json.load(f)["counts"]

# 2. Visszafejtés (az i-edik lefutott mérés a table[order[i]] áramkörhöz tartozik)
circuits_by_id = {}
for i, orig_idx in enumerate(order):
    spec = table[orig_idx]
    circuits_by_id[spec["circuit_id"]] = {
        "spec": spec,
        "counts": raw_counts[i]
    }
```

---

## 8. Időbélyegek és Audit-Trail Transzparencia

- **Máté jóslatának rögzítése (Gate 6 commit `3bbee7f`):** 2026-11-18 18:21:07 UTC
- **QPU beküldés (Gate 7 job `dbuupiv82tmc73du4u70`):** 2026-11-18 18:21:38 UTC (31 másodperccel a jóslat után)
- **Megjegyzés:** Mivel a repó egyben lett pusholva a GitHubra a mérés után, külső szemlélő számára a megelőzés hitelességét a git commit időbélyege és az IBM Quantum rendszerében rögzített job létrehozási idő garantálja.
