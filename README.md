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

## Rung 3 (done): AC0 #SAT via a restriction tree

The mechanism restriction families (Impagliazzo–Matthews–Paturi, SODA 2012)
formalize, in its deterministic skeleton: restrict variables one at a time
(most-live-occurrences pivot), let the circuit collapse under three-valued
evaluation, and add 2^(free) the moment the root is decided. All savings
over 2^n are early collapse — the switching behavior itself. The full IMP
machinery (random restrictions with switching-lemma bookkeeping and provable
worst-case savings) is **not** implemented; what is measured is the
empirical savings of the same mechanism. The strict two-valued brute-force
evaluator shares no code with the engine and must agree on the exact count.

```bash
$EIGS tests/test_restriction.eigs        # rung gate: 26 assertions
$EIGS polymethod.eigs ac0 14 28 3 1      # one instance, vs brute force
$EIGS polymethod.eigs ac0-sweep 1        # the fan-in sweep
```

### The measured artifact — savings vs bottom fan-in

Random k-CNF, n=16, m=32, seed 1, exact counts oracle-verified:

| bottom fan-in k | tree leaves | 2^16 | structural savings |
|---|---|---|---|
| 2 | 51 | 65,536 | 1285x |
| 3 | 1,109 | 65,536 | 59x |
| 4 | 7,092 | 65,536 | 9.2x |
| 5 | 12,856 | 65,536 | 5.1x |

Savings degrade steeply as bottom fan-in grows — the switching-lemma
prediction made visible in four rows. A depth-3 OR∘AND∘OR instance decides
in 13 leaves; at n=24 (engine only, brute unaffordable) a 3-CNF counts
10,023 solutions visiting 26,058 leaves of 2^24 = 16.7M (644x). Honest
caveat the data itself shows: each tree node pays an O(circuit) analyze
pass, so *wall-clock* advantage erodes faster than leaf savings (at k=5
the two sides run at wall parity while leaves still save 5.1x) — leaves
is the clean measure of the restriction mechanism; wall time bundles in
the interpreter's per-node constant.

## Rung 4 (done): AC0[⊕] #SAT via F2 probabilistic polynomials

The constructive core of Rajgopal–Santhanam–Srinivasan (MFCS 2018): each
OR/AND gate becomes Razborov's degree-t probabilistic polynomial over F2
(1 ⊕ ∏(1 ⊕ Σ_{S_i} children), seeded subset sums), XOR gates are exact,
the composition is one multilinear F2 polynomial per seed, and each
polynomial is evaluated on **all 2^n inputs** by the F2 version of rung
1's subset-lattice zeta transform. A per-input majority over r seeds
estimates the truth table and the count. RSS's actual contribution —
derandomizing the seeds via small-bias spaces — is **not** implemented;
seeds come from the repo's LCG (reproducible, not derandomized). The
strict evaluator with XOR support is the shared-code-free exact oracle.

```bash
$EIGS tests/test_ac0xor.eigs        # rung gate: 12 assertions
$EIGS polymethod.eigs ac0x-sweep    # the error-vs-degree sweep
```

### The measured artifact — the error/degree tradeoff

Pure Razborov unit (one OR of 6 literals, n=8, mean over 5 seeds):
mismatches fall 124 → 60 → 28 → 15.2 → 7.2 → 5.6 of 256 for t = 1..6 —
the 2^(-t) decay, halving per degree step, in six rows. On a composed
depth-3 XOR∘AND∘OR circuit (n=10, 9 approximated gates) single seeds stay
noisy exactly as the union bound over gates predicts (the parity top gate
makes every gate error visible), and at t=8 with a 9-seed majority the
count goes **exact** — verified equal to brute force on three circuit
seeds with zero truth-table mismatches. Notable measured detail: F2
cancellation keeps the composed polynomials tiny at these sizes (max 27
monomials at t=8) — the degree grows, the support doesn't.

## Rung 5 (done): depth-2 threshold SAT via sampled-threshold PTFs

The baseline member of the Alman–Williams / Alman–Chan–Williams PTF family:
each MAJ gate is replaced by the *sampled* threshold (s of its k inputs,
seeded, threshold rescaled) expanded **exactly** as a multilinear integer
polynomial via the symmetric-function Möbius expansion
(α_j = Σ_{i≤j} (−1)^{j−i} C(j,i) [i ≥ θ]); the top gate's expansion is
substituted with the bottom-gate polynomials. The result is one integer
polynomial, provably 0/1-valued on every input, evaluated on all 2^n
inputs by the **integer** subset-lattice zeta transform — rung 1's engine
in its third ring (counts, F2, now Z). At s = k the construction is exact,
which anchors the differential; ACW's actual n^(1/3)-degree
Chebyshev-plus-recursion machinery is **not** implemented — this rung
measures the baseline it improves on.

```bash
$EIGS tests/test_thr2.eigs           # rung gate: 16 assertions
$EIGS polymethod.eigs thr2 12 4 5 1  # one circuit, full-sample, vs brute
$EIGS polymethod.eigs thr2-sweep     # error + support sweeps
```

### The measured artifacts

**The empirical open from the hq report — does the support stay under the
2^(n/2) budget ACW's rectangle evaluation needs? — answers NO for the
baseline**, with numbers (n=14, k=5, full-sample exact builds, every row
oracle-verified):

| bottom gates m | monomials | budget 2^7 | over budget |
|---|---|---|---|
| 4 | 289 | 128 | 2.3x |
| 6 | 3,838 | 128 | 30x |
| 8 | 4,780 | 128 | 37x |
| 12 | 5,851 | 128 | 46x |

Support is governed by circuit size, not n (fixed m=4: ~300 monomials
flat from n=10 to 16 while the budget grows past it) — and it crosses the
budget as soon as the circuit has more than a handful of gates. This is
the quantified reason ACW's low-degree machinery must exist: the naive
exact expansion cannot ride the 2^(n/2) rectangle. Integer coefficients
grow too (max 84 at m=12) — the bigint pressure point GAPS.md predicted,
still comfortably under double precision at demo scale.

**The sampling-error curve is non-monotone** (n=10, k=5, mean of 5 seeds):
150.4 mismatches at s=3, **228.6 at s=4**, 0 at s=5 — because the rescaled
threshold ⌈θ·s/k⌉ rounds hardest at s=4 (3-of-4 vs the true 3-of-5).
At tiny sample sizes the rounding bias dominates the concentration
behavior entirely. The suite asserts only the verified endpoints (exact at
full sample, errs when undersampled) — monotonicity would be a false test.

## The ladder (from the hq research report, easiest → frontier)

| rung | artifact | status |
|---|---|---|
| 1 | SYM∘AND evaluation engine (zeta transform) | **done** |
| 2 | Split-and-list MAX-2-SAT with a *measured* brute-force crossover | **done** |
| 3 | AC0 #SAT via a restriction tree (savings-vs-fan-in measured) | **done** |
| 4 | AC0[⊕] #SAT via F2 probabilistic polynomials (error-vs-degree measured) | **done** |
| 5 | Depth-2 threshold SAT via sampled-threshold PTFs (support-vs-budget measured) | **done** |
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
