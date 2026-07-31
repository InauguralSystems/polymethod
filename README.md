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
| 2 | Split-and-list MAX-2-SAT with a *measured* brute-force crossover | next |
| 3 | AC0 #SAT via restriction families | planned |
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
