#!/usr/bin/env python3
"""
test_geometry_fidelity.py — Graph fidelity & unitary preservation tests
Gate 1 validation for Quantum Time Crystal Ring.
"""

import networkx as nx
import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, state_fidelity, Statevector

def verify_ring_topology(nodes, edges):
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    
    # 1. Vertex count
    if len(G.nodes) != 12:
        return False, "Node count != 12"
    # 2. Edge count
    if len(G.edges) != 12:
        return False, "Edge count != 12"
    # 3. Regular degree 2
    if not all(d == 2 for _, d in G.degree()):
        return False, "Not all vertices have degree 2"
    # 4. Connected and exactly one cycle of length 12
    if not nx.is_connected(G):
        return False, "Graph is not connected"
    cycles = nx.cycle_basis(G)
    if len(cycles) != 1 or len(cycles[0]) != 12:
        return False, "Graph does not have exactly one 12-cycle"
    return True, "Valid C12 ring"

def verify_triangle_topology(nodes, edges):
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    
    if len(G.nodes) != 3 or len(G.edges) != 3:
        return False, "Nodes or edges != 3"
    if not all(d == 2 for _, d in G.degree()):
        return False, "Not all vertices have degree 2"
    if not nx.is_connected(G):
        return False, "Graph is not connected"
    cycles = nx.cycle_basis(G)
    if len(cycles) != 1 or len(cycles[0]) != 3:
        return False, "Graph does not have exactly one 3-cycle"
    return True, "Valid C3 triangle"

def test_12_ring_topology():
    ring = [131, 132, 133, 134, 135, 139, 155, 154, 153, 152, 151, 138]
    edges = [(ring[i], ring[(i+1)%12]) for i in range(12)]
    valid, msg = verify_ring_topology(ring, edges)
    assert valid, msg

def test_triangle_topology():
    nodes = [0, 1, 2]
    edges = [(0, 1), (1, 2), (2, 0)]
    valid, msg = verify_triangle_topology(nodes, edges)
    assert valid, msg

def test_negative_star_graph_rejected():
    # A star graph: center node 0, spokes to 1, 2, 3 (no ring edges)
    nodes = [0, 1, 2, 3]
    edges = [(0, 1), (0, 2), (0, 3)]
    
    # Must be rejected by ring check
    valid_ring, _ = verify_ring_topology(nodes, edges)
    assert not valid_ring, "Star graph was erroneously accepted as a ring!"
    
    # Must be rejected by triangle check
    valid_tri, _ = verify_triangle_topology(nodes, edges)
    assert not valid_tri, "Star graph was erroneously accepted as a triangle!"

def test_floquet_unitary_fidelity_triangle():
    """Verify that synthetic triangle circuit with roundtrip SWAP is unitarily identical to logical triangle."""
    # Logical triangle circuit (ideal 3 qubits)
    qc_ideal = QuantumCircuit(3)
    # Layer 1: RX pulse
    qc_ideal.rx(0.9 * np.pi, range(3))
    # Layer 2: RZZ edges (0-1, 1-2, 2-0)
    qc_ideal.rzz(0.4, 0, 1)
    qc_ideal.rzz(0.4, 1, 2)
    qc_ideal.rzz(0.4, 2, 0)
    # Layer 3: RZ disorder
    qc_ideal.rz(0.1, 0)
    qc_ideal.rz(-0.2, 1)
    qc_ideal.rz(0.15, 2)

    # Physical implementation using linear chain 0-1-2 with roundtrip SWAP for edge (0,2)
    qc_synth = QuantumCircuit(3)
    qc_synth.rx(0.9 * np.pi, range(3))
    qc_synth.rzz(0.4, 0, 1)
    qc_synth.rzz(0.4, 1, 2)
    # SWAP 1-2 so qubit 2 moves to position 1 (adjacent to 0)
    qc_synth.swap(1, 2)
    qc_synth.rzz(0.4, 0, 1) # acts on logical 0 and 2
    qc_synth.swap(1, 2)     # restore layout
    qc_synth.rz(0.1, 0)
    qc_synth.rz(-0.2, 1)
    qc_synth.rz(0.15, 2)

    op_ideal = Operator(qc_ideal)
    op_synth = Operator(qc_synth)
    
    # Equivalent up to global phase: Tr(A^\dagger B) / d has magnitude 1
    d = 2**3
    overlap = (op_ideal.data.conj().T @ op_synth.data).trace() / d
    fidelity = np.abs(overlap) ** 2
    assert np.isclose(fidelity, 1.0, atol=1e-7), f"Unitary fidelity {fidelity} != 1.0"
