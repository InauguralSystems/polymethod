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
  n=16/m=4000: 0 mismatches. The 1e8-iteration ceiling still applies when
  running against the v0.33.0 CI pin — lift it when the pin moves past the
  next release.
- **Rung-1 build friction was near zero (2026-07-30).** The engine needed
  `bit_and`/`bit_or`/`bit_xor`/`bit_shl` (present as builtins), stdlib
  `lib/int_vector.eigs` buffers for the 2^n count vectors, and `%`. Nothing
  had to be worked around. The interesting pressure starts at rung 2:
  split-and-list needs sorting 2^(2n/3)-scale keyed records and a deliberate
  peak-memory cliff — watch list-of-pairs vs parallel int_vector shapes there.
- **Counting range (future).** Numbers are doubles: monomial counts and
  intermediate sums are exact only below 2^53. Fine for every planned rung at
  demo n, but rung 6's exact-monomial-count artifact must check its totals
  against that bound explicitly; if a real count would exceed it, that is a
  bigint upstream conversation, not a local workaround.
- **2^n int_vector allocation (watch).** `int_vector_new of 2^20` is a single
  large buffer; rung 2 will want several at once plus sort scratch. The 4GB
  dev boxes are the thrash detector — instrument peak memory before scaling n.
