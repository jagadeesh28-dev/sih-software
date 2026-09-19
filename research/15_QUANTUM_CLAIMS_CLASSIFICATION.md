# 15 — QUANTUM CLAIMS: WHAT IS AND IS NOT QUANTUM
## RQ20: Distinguishing Quantum-Inspired from Quantum Computing

---

## 1. The Terminology Problem

The term "quantum-inspired" is widely misused in optimization literature and commercial contexts. This document provides clear, scientifically defensible definitions for use in SIH26138 publications.

---

## 2. True Quantum Computing

**Definition:** Computational paradigm that exploits:
- **Qubits** (quantum bits): physical two-level quantum systems (superconducting circuits, trapped ions, photons)
- **Superposition:** a qubit can be in a superposition of |0⟩ and |1⟩ simultaneously
- **Entanglement:** correlations between qubits that cannot be described classically
- **Interference:** quantum amplitudes add/cancel, enabling algorithmic speedup

**Hardware:** IBM Quantum, Google Sycamore, IonQ, Quantinuum, Rigetti (as of 2025)

**Algorithms with proven quantum advantage:**
- Grover's algorithm: $O(\sqrt{N})$ search vs. classical $O(N)$
- Shor's algorithm: polynomial factoring vs. classical exponential
- HHL algorithm: linear systems (with caveats)

**Current limitations:** NISQ (Noisy Intermediate-Scale Quantum) era: <1000 qubits, high error rates, decoherence. No practical quantum advantage for general optimization as of 2025.

---

## 3. Quantum-Inspired Algorithms (Our Category)

**Definition:** Classical algorithms that borrow mathematical constructs from quantum mechanics — such as probability amplitudes, superposition, interference — and implement them on conventional CPUs/GPUs.

**Key distinction:** Quantum-inspired algorithms:
- Run entirely on classical hardware (no quantum computer required)
- Do not use physical qubits
- Do not provide quantum speedup in the complexity-theoretic sense
- Use quantum mathematical formalism as a heuristic design principle

**Why "inspired"?**
- QPSO: "quantum" refers to the quantum delta-potential well model used to derive position updates. The actual computation is floating-point arithmetic on a CPU.
- QIEA: "quantum" refers to Q-bits (classical probability amplitude vectors, not physical qubits). The rotation gate is matrix multiplication, not a physical quantum gate.
- QUBO/annealing: solvers on classical digital annealers (Fujitsu DA) are classical hardware; the "quantum" is in the Ising model formulation.

---

## 4. What SIH26138 Uses (Precise Classification)

| Component | Classification | Hardware |
|:---|:---|:---|
| QPSO | Quantum-Inspired Swarm Intelligence | Classical CPU |
| QIEA | Quantum-Inspired Evolutionary Algorithm | Classical CPU |
| Hybrid QI-HFO | Quantum-Inspired Hybrid | Classical CPU |
| Q-bit (binary) | Classical probability amplitude | Mathematical abstraction |
| Dirichlet-Q vector | Classical probability distribution | Mathematical abstraction |
| Quantum rotation gate | 2×2 matrix multiplication | Classical CPU |

**None of the SIH26138 components require or use quantum hardware.**

---

## 5. Scientifically Defensible Language

### Acceptable Statements

✅ "We propose a quantum-inspired heterogeneous fleet optimizer that employs Q-bit representations from the QIEA framework to handle binary and categorical decision variables."

✅ "The quantum-behaved particle swarm optimization (QPSO) algorithm models particle dynamics using a quantum delta-potential well analogy on classical hardware."

✅ "Our approach draws on quantum mechanical principles — specifically, probability amplitude representations and rotation gate updates — to design more diverse search operators for mixed-variable optimization."

✅ "Unlike true quantum computing approaches, our algorithm runs on standard CPUs and requires no quantum hardware."

### Unacceptable Statements

❌ "Our algorithm achieves quantum speedup." — False; no quantum speedup claim is valid for classical algorithms.

❌ "We use qubits." — Misleading; we use classical probability amplitude vectors called Q-bits.

❌ "Our algorithm is inherently quantum." — False; all computations are classical.

❌ "The quantum-inspired approach exploits quantum entanglement." — False; there is no physical entanglement in classical QIEA.

---

## 6. IMO / SIH Context Note

For SIH 2026 presentations and maritime industry audiences:
- Lead with the practical value: "reduces fuel cost and emissions through intelligent optimization"
- Mention "quantum-inspired" as a descriptor of the algorithmic approach, not as a claim of quantum computing advantage
- Emphasize that the algorithm runs on standard hardware and can be deployed without quantum infrastructure
- The "quantum-inspired" label legitimately differentiates from classical GA or PSO in terms of the underlying mathematical framework

---

## 7. No Free Lunch and Quantum-Inspired Claims

The **No Free Lunch theorem** (Wolpert & Macready 1997) states that over all possible optimization problems, all algorithms perform equally. This means:

- Quantum-inspired algorithms are NOT universally superior to classical algorithms
- They may be better for specific problem classes (sparse, combinatorial, early-exploration-dominated)
- They may be worse for others (smooth, unimodal, gradient-rich)

For the SIH26138 problem specifically:
- QIEA's Q-bit representation is appropriate for binary/categorical variables
- QPSO's continuous search is appropriate for speed optimization
- DE's difference-vector mutation is competitive for all variable types but less specialized

**The claim is not "QI is better" — it is "QI is more appropriate for the structural features of this specific problem."** This is a defensible, nuanced, and scientifically honest claim.
