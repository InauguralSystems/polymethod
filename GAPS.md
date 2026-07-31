# polymethod Gap Log

Every entry should be tied to a concrete build or benchmark friction.
Root EigenScript issues get fixed upstream instead of worked around here.

## Open Watchlist

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
