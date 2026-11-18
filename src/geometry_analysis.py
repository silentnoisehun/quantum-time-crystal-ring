#!/usr/bin/env python3
"""
geometry_analysis.py — Topology, girth, and ring selection on IBM Heron (ibm_marrakesh)
Gate 1 of Quantum Time Crystal Ring protocol.
"""

import json
import math
from pathlib import Path
import networkx as nx
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService

REPO = Path(__file__).resolve().parent.parent

def load_backend():
    token_file = r"C:\Users\mater\Downloads\apikey (1) (1).json"
    with open(token_file, encoding="utf-8") as f:
        token = json.load(f)["apikey"]
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token, instance="open-instance")
    backend = service.backend("ibm_marrakesh")
    return backend

def analyze_coupling_graph(backend):
    G = nx.Graph()
    for u, v in backend.coupling_map:
        G.add_edge(u, v)

    # Check 3-cycles
    basis = nx.cycle_basis(G)
    triangles = [c for c in basis if len(c) == 3]
    cycle_lengths = [len(c) for c in basis]
    girth = min(cycle_lengths) if cycle_lengths else 0

    # Find all induced 12-cycles (hexagons)
    # On heavy-hex, basis 12-cycles are the elementary hexagons
    basis_12 = [c for c in basis if len(c) == 12]
    rings = []
    for c in basis_12:
        sub = G.subgraph(c)
        if sub.number_of_edges() == 12 and all(d == 2 for _, d in sub.degree()):
            # Order the nodes along the cycle
            ordered = list(nx.find_cycle(sub))
            ordered_nodes = [e[0] for e in ordered]
            rings.append(ordered_nodes)

    return G, len(triangles), girth, rings

def score_rings(backend, rings):
    props = backend.properties(refresh=True)
    target = backend.target

    scored = []
    for r_idx, ring in enumerate(rings):
        # Edges in order
        ring_edges = [(ring[i], ring[(i + 1) % len(ring)]) for i in range(len(ring))]
        
        cz_errors = []
        for u, v in ring_edges:
            # Check CZ error in props
            err = None
            try:
                err = props.gate_error("cz", [u, v])
            except Exception:
                try:
                    err = props.gate_error("cz", [v, u])
                except Exception:
                    pass
            if err is None:
                err = 0.01  # fallback default if uncalibrated
            cz_errors.append(err)

        ro_errors = []
        for q in ring:
            try:
                ro = props.readout_error(q)
            except Exception:
                ro = 0.02
            ro_errors.append(ro)

        cz_sum = sum(cz_errors)
        ro_sum = sum(ro_errors)
        total_score = cz_sum + ro_sum

        scored.append({
            "ring_index": r_idx,
            "nodes": ring,
            "cz_error_sum": round(float(cz_sum), 6),
            "readout_error_sum": round(float(ro_sum), 6),
            "total_score": round(float(total_score), 6),
            "max_cz_error": round(float(max(cz_errors)), 6),
            "max_ro_error": round(float(max(ro_errors)), 6),
        })

    # Sort by total_score ascending (lowest error wins)
    scored.sort(key=lambda x: x["total_score"])
    return scored

def evaluate_triangle_variants(backend):
    # Pick a clean 3-qubit linear path on backend
    # Let's find a 3-qubit path a-b-c with lowest error
    best_path = [151, 138, 131]  # from candidate ring
    a, b, c = best_path

    # Build 1 Floquet cycle interaction layer RZZ(a,b), RZZ(b,c), RZZ(c,a)
    # Variant 1: Explicit round-trip SWAP
    qc_v1 = QuantumCircuit(3)
    qc_v1.rzz(0.5, 0, 1)  # a-b
    qc_v1.rzz(0.5, 1, 2)  # b-c
    qc_v1.swap(1, 2)
    qc_v1.rzz(0.5, 0, 1)  # logical a-c
    qc_v1.swap(1, 2)
    t_v1 = transpile(qc_v1, backend=backend, initial_layout=[a, b, c], optimization_level=1)
    cz_v1 = t_v1.count_ops().get("cz", 0)

    # Variant 2: Tracked permutation (one SWAP, logical frame rotated)
    qc_v2 = QuantumCircuit(3)
    qc_v2.rzz(0.5, 0, 1)
    qc_v2.rzz(0.5, 1, 2)
    qc_v2.swap(1, 2)
    qc_v2.rzz(0.5, 0, 1)
    t_v2 = transpile(qc_v2, backend=backend, initial_layout=[a, b, c], optimization_level=1)
    cz_v2 = t_v2.count_ops().get("cz", 0)

    # Variant 3: Transpiler optimal synthesis
    qc_v3 = QuantumCircuit(3)
    qc_v3.rzz(0.5, 0, 1)
    qc_v3.rzz(0.5, 1, 2)
    qc_v3.rzz(0.5, 0, 2)
    t_v3 = transpile(qc_v3, backend=backend, initial_layout=[a, b, c], optimization_level=3)
    cz_v3 = t_v3.count_ops().get("cz", 0)

    # Open path reference (a-b and b-c only, no closing edge)
    qc_path = QuantumCircuit(3)
    qc_path.rzz(0.5, 0, 1)
    qc_path.rzz(0.5, 1, 2)
    t_path = transpile(qc_path, backend=backend, initial_layout=[a, b, c], optimization_level=1)
    cz_path = t_path.count_ops().get("cz", 0)

    return {
        "path_qubits": [a, b, c],
        "variant1_roundtrip_swap_cz": cz_v1,
        "variant2_tracked_swap_cz": cz_v2,
        "variant3_compiler_synthesized_cz": cz_v3,
        "open_path_cz": cz_path
    }

def main():
    print("=" * 70)
    print("GATE 1: GEOMETRY & GRAPH FIDELITY ANALYSIS ON IBM_MARRAKESH")
    print("=" * 70)

    backend = load_backend()
    print(f"Backend loaded: {backend.name} (Qubits: {backend.num_qubits})")

    G, num_triangles, girth, rings = analyze_coupling_graph(backend)
    print(f"Girth (shortest cycle length): {girth}")
    print(f"Native 3-cycles found: {num_triangles}")
    print(f"Native 12-qubit regular rings found: {len(rings)}")

    scored_rings = score_rings(backend, rings)
    best_ring = scored_rings[0]
    print(f"\nWinning 12-qubit Ring: {best_ring['nodes']}")
    print(f"Total error score: {best_ring['total_score']} (CZ sum: {best_ring['cz_error_sum']}, RO sum: {best_ring['readout_error_sum']})")

    triangle_results = evaluate_triangle_variants(backend)
    print("\nTriangle Implementations CZ Counts per Floquet Cycle:")
    print(f"  Variant 1 (Roundtrip SWAP): {triangle_results['variant1_roundtrip_swap_cz']} CZ")
    print(f"  Variant 2 (Tracked SWAP)  : {triangle_results['variant2_tracked_swap_cz']} CZ")
    print(f"  Variant 3 (Compiler synth): {triangle_results['variant3_compiler_synthesized_cz']} CZ")
    print(f"  Open Path (Reference)    : {triangle_results['open_path_cz']} CZ")

    report = {
        "backend": backend.name,
        "qubits": backend.num_qubits,
        "date_utc": "2026-11-18T17:48:00Z",
        "date_budapest": "2026-11-18T18:48:00+01:00",
        "topology": {
            "girth": girth,
            "native_3_cycles_count": num_triangles,
            "total_12_rings_count": len(rings),
            "winning_ring": best_ring,
            "all_scored_rings": scored_rings
        },
        "triangle_comparison": triangle_results
    }

    out_file = REPO / "results" / "geometry_report.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nSaved geometry report to: {out_file}")

if __name__ == "__main__":
    main()
