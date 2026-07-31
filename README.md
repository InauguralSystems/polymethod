# polymethod

The algorithmic method (the Williams program) as executable,
differentially-tested artifacts, written in EigenScript.

Circuit-analysis algorithms that beat brute force are the modern route to
circuit lower bounds: a SAT/#SAT algorithm with superpolynomial savings for a
circuit class implies the class cannot compute everything in NEXP. The
literature contains a ladder of such algorithms — and, as of July 2026, **zero
implementations of any of them, anywhere**. This repo climbs the ladder one
rung at a time, with every stage tested against an external brute-force
oracle and a planted fault proving the gate actually gates.

It is an *instrument*, twice over:

1. **Pointed at the theory.** Each rung produces measured artifacts no paper
   contains (real crossover points, exact converted-circuit sizes, empirical
   boundary constants). The research record behind the rung selection lives in
   the org's hq repo (`reports/tc0-sat-frontier-2026-07-30.md`).
2. **Pointed at EigenScript.** Exact combinatorial arithmetic at scale — giant
   monomial dictionaries, modular hot loops, 2^n enumeration, deliberate
   memory cliffs — is a runtime surface no other consumer stresses. Language
   friction goes in `GAPS.md` and upstream, never worked around silently.

**Honest ceiling:** this repo demonstrates and measures known algorithms and
localizes the missing objects in running code. It proves no lower bound and
settles nothing.

## Rung 1 (current): the SYM∘AND evaluation engine

A SYM∘AND ("SYM+") circuit is a list of AND monomials feeding a symmetric
output function of the satisfied-monomial count. It is the normal form that
made ACC0 fall: Yao–Beigel–Tarui converts any ACC0 circuit into one. The
engine evaluates the count on **all 2^n inputs** in O(2^n · n) total time via
the subset-lattice zeta transform (the `h = x·h1 + h2` recursion of Williams,
CCC 2011, Lemma 4.2) — vs O(2^n · m) for direct evaluation. That "evaluate
everywhere, fast" primitive is the engine inside the ACC0-SAT algorithm.

```bash
EIGS=${EIGENSCRIPT_BIN:-../EigenScript/src/eigenscript}

$EIGS tests/test_symplus.eigs        # milestone gate: 40 assertions
$EIGS polymethod.eigs                # demo: n=12, m=60, seeded
$EIGS polymethod.eigs 18 400 3       # n=18, 400 monomials, seed 3
```

Single illustrative run on the dev box (not an n=5 perf claim): at n=18,
m=400, the engine takes ~3.8s against the oracle's ~54s — the transform's
m/n advantage showing through, oracle-checked to byte equality on all 2^18
outputs.

## Rung 2 (done): split-and-list MAX-2-SAT, with the crossover measured

Williams (TCS 348, 2005): split the n variables into three parts, list the
2^(n/3) partial assignments of each, precompute the three pairwise
clause-weight tables (the O(2^(2n/3))-memory objects), and find the optimum
as a maximum-weight triangle over weight splits (k01, k02, k12). The
triangle inner step uses bit-packed Boolean row masks — the practical
stand-in for the fast-matrix-multiplication call, which the theory needs
only existentially.

```bash
$EIGS tests/test_split_list.eigs             # rung gate: 38 assertions
$EIGS polymethod.eigs max2sat 12 36 1        # one size, vs brute + certificate
$EIGS polymethod.eigs max2sat-sweep 1        # the crossover sweep
```

Two oracles guard every result: brute-force 2^n enumeration (shared-code-free)
must agree on the optimum, and the winning triangle is decoded into a full
assignment and re-evaluated clause-by-clause — a **certificate** that must
equal the claimed optimum. The suite plants a corrupted weight-table entry
and asserts the certificate catches it.

### The measured artifact

The "beats brute force at n≈45–60" folklore (uncited in the literature —
see the hq research report) does **not** describe a same-runtime pair. On
this box (seed 1, m = 3n, single runs — counters are deterministic):

| n | table entries | split-and-list | brute force | ratio |
|---|---|---|---|---|
| 9 | 192 | 17 ms | 36 ms | 2.1x |
| 12 | 768 | 49 ms | 327 ms | 6.7x |
| 15 | 3,072 | 223 ms | 3.2 s | 14x |
| 18 | 12,288 | 1.1 s | 30.3 s | 28x |
| 21 | 49,152 | 4.6 s | 281 s | 61x |

The crossover is **below n=9**, and the ratio doubles every +3 variables —
the 2^(n/3) separation the theory predicts, with split-and-list wall time
tracking its 2^(2n/3) table build (×~4.3 per step) and the packed-word
triangle search contributing almost nothing at these sizes (word_ops ≤
1,407). The folklore n≈45–60 figure is about optimized-C constants and the
ω-exponent matmul term, neither of which is in play at demo scale; in a
constant-factor-fair fight the asymptotics win immediately. Memory is the
real wall, as predicted: table entries grow ×4 per +3 variables, projecting
the 4 GB cliff at n ≈ 42 on this box — before wall-clock ever becomes the
binding constraint.

### The oracle discipline

- `brute_counts` shares no code with the engine: it evaluates the circuit
  definition directly, one input at a time.
- Every engine run is compared on the **full 2^n output vector**, not a
  summary statistic.
- The suite plants two faults (a dropped monomial, a flipped table entry) and
  asserts the differential **fails** — the checker is itself checked.
- Instance generation is seeded (in-repo minstd LCG), so every result is
  reproducible bit-for-bit; no runtime randomness anywhere.

## The ladder (from the hq research report, easiest → frontier)

| rung | artifact | status |
|---|---|---|
| 1 | SYM∘AND evaluation engine (zeta transform) | **done** |
| 2 | Split-and-list MAX-2-SAT with a *measured* brute-force crossover | **done** |
| 3 | AC0 #SAT via restriction families | next |
| 4 | AC0[⊕] deterministic #SAT (derandomized F2 polynomials) | planned |
| 5 | ACW depth-2 threshold SAT (probabilistic PTFs) | planned |
| 6 | Toy YBT/Chen–Papakonstantinou conversion, per-stage only | planned |
| 7 | Chen–Tal–Wang estimator chain (the live frontier) | aspiration |

End-to-end ACC0-SAT is deliberately **not** a goal: the conversion is galactic
at any demo scale (~2^1000 monomials for a toy circuit). Rungs are tested
per-stage, against oracles, at sizes where the oracle is affordable.

## Toolchain

EigenScript is not vendored. Point at a built binary via `EIGENSCRIPT_BIN`
(default `../EigenScript/src/eigenscript`). CI pins the runtime via
`.devcontainer/Dockerfile`'s `EIGS_REF`. Run everything from the repo root —
load paths are cwd-relative.

## License

MIT.
