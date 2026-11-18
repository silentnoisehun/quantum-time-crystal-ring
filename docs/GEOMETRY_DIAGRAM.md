# Layout and Graph Topology Diagrams for Máté's Approval

**Target Backend:** `ibm_marrakesh` (Heron r2, 156 qubits)  
**Verification Date:** 2026-11-18 17:48 UTC (18:48 Budapest)

---

## 1. Native 12-Qubit Hexagonal Ring ($C_{12}$)

Optimal ring on `ibm_marrakesh` selected by minimum error score ($\text{CZ}_\text{sum} = 0.0645$, $\text{RO}_\text{sum} = 0.4150$):

```
                 [Q133] ━━━━━ [Q134]
                ╱                   ╲
            [Q132]                 [Q135]
              ┃                       ┃
            [Q131]                 [Q139]
              ┃                       ┃
            [Q138]                 [Q155]
                ╲                   ╱
                 [Q151] ━━━━━ [Q152] ━━━━━ [Q153] ━━━━━ [Q154]
```
*(Exact loop order: 131 - 132 - 133 - 134 - 135 - 139 - 155 - 154 - 153 - 152 - 151 - 138 - 131)*

- **Topology properties:**
  - Vertices: 12
  - Edges: 12 (all native Heron two-qubit couplers, zero SWAPs required)
  - Coordination degree: exactly 2 for every site (closed boundary-free loop)
  - Girth of device: 12

---

## 2. 3-Qubit Triangle ($C_3$) via Synthetic SWAP Routing

Physical transmon path: `[Q151] ━━━━━ [Q138] ━━━━━ [Q131]`

```
           [Q131]
          ▲      ▲
         ╱        ╲  (Synthetic Edge via roundtrip SWAP)
        ╱          ╲
     [Q138] ━━━━━ [Q151]
```

- **Physical edges:**
  - Native Edge 1: `(151, 138)`
  - Native Edge 2: `(138, 131)`
  - Synthetic Edge 3: `(151, 131)` realized by `SWAP(138, 131) + RZZ(151, 138) + SWAP(138, 131)`
- **CZ Cost per Floquet Cycle:**
  - Triangle Variant 1 (Explicit roundtrip SWAP): 12 CZ
  - Triangle Variant 2 (Tracked permutation SWAP): 9 CZ
  - Triangle Variant 3 (Compiler synthesized): 9 CZ
  - Open Linear Path Control ($a-b$, $b-c$ only): 4 CZ
