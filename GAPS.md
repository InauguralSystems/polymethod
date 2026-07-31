# polymethod Gap Log

Every entry should be tied to a concrete build or benchmark friction.
Root EigenScript issues get fixed upstream instead of worked around here.

## Open Watchlist

- **UPSTREAM BUG FOUND DAY ONE (2026-07-31): silent loop truncation at 1e8
  cumulative iterations — EigenScript #772.** The rung-1 full-vector
  differential flagged 4 wrong outputs in 524,288 at n=19, m=1000; an
  independent Python third implementation proved the *brute-force oracle
  side* wrong — the runtime's default sandbox loop cap (100,000,000, active
  outside any sandbox) silently breaks the running loop every 1e8 cumulative
  iterations. Deterministic, tier-independent (reproduces under
  `EIGS_JIT_OFF=1`); corrupted indices follow the predicted arithmetic
  progression (spacing 1e8 / iterations-per-outer). Minimal repro: a single
  loop to 1.5e8 stops at exactly 1e8 with exit 0. `tests/probe_mismatch.eigs`
  is the locating tool. **FIXED upstream 2026-07-31** (EigenScript PR #773,
  `72c85e0`): the cap now fires only under an armed sandbox budget, and the
  counter widened to 64-bit. Differential re-run at n=19/m=1000 and
  n=16/m=4000: 0 mismatches. Shipped in v0.34.0; with the CI pin now at
  v0.34.0 the 1e8-iteration ceiling is LIFTED — oracle runs may exceed 1e8
  cumulative iterations everywhere.
- **Rung-2 friction (2026-07-31): bitset ops are hand-rolled.** The packed
  Boolean row masks needed 24-bit word packing (`bit_or`/`bit_shl` per bit),
  a manual lowest-set-bit loop to recover the witness, and manual `i*N+j`
  2D indexing over `int_vector`. All workable, none pretty. If a later rung
  (ACW's probabilistic-PTF matrices, rung 5) leans harder on Boolean linear
  algebra, the upstream asks crystallize as: a native fixed-width bitset
  (or `popcount`/`ctz` builtins) and possibly 2D buffer views. Logged as
  pressure, not yet worth an upstream issue — one more rung of evidence
  first (the house rule: the data decides).
- **Rung-2 measured result worth carrying:** same-runtime crossover vs brute
  force is below n=9 (ratio doubles per +3 vars, = 2^(n/3)); wall time is
  table-build-dominated (2^(2n/3)), word_ops negligible at demo scale; the
  4 GB memory cliff projects to n≈42 — memory binds before time does, as
  the proposal predicted.
- **Rung-1 build friction was near zero (2026-07-30).** The engine needed
  `bit_and`/`bit_or`/`bit_xor`/`bit_shl` (present as builtins), stdlib
  `lib/int_vector.eigs` buffers for the 2^n count vectors, and `%`. Nothing
  had to be worked around.
- **Counting range (future).** Numbers are doubles: monomial counts and
  intermediate sums are exact only below 2^53. Fine for every planned rung at
  demo n, but rung 6's exact-monomial-count artifact must check its totals
  against that bound explicitly; if a real count would exceed it, that is a
  bigint upstream conversation, not a local workaround.
- **2^n int_vector allocation (watch).** `int_vector_new of 2^20` is a single
  large buffer; rung 2 will want several at once plus sort scratch. The 4GB
  dev boxes are the thrash detector — instrument peak memory before scaling n.
