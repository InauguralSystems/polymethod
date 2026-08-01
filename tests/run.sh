#!/usr/bin/env bash
# polymethod milestone gate. Exit 0 iff every assertion holds.
# EIGS=<eigenscript> overrides the binary (CI passes EIGS=eigenscript).
set -u
HERE="$(cd "$(dirname "$0")/.." && pwd)"
cd "$HERE"
EIG="${EIGS:-../EigenScript/src/eigenscript}"

echo "== rung 1: SYM∘AND engine vs brute-force oracle =="
"$EIG" tests/test_symplus.eigs || exit 1

echo "== rung 2: split-and-list MAX-2-SAT vs brute force + certificate =="
"$EIG" tests/test_split_list.eigs || exit 1

echo "== rung 3: restriction-tree AC0 #SAT vs brute force =="
"$EIG" tests/test_restriction.eigs || exit 1

echo "== rung 4: F2-polynomial AC0[xor] #SAT vs brute force =="
"$EIG" tests/test_ac0xor.eigs || exit 1

echo "== rung 5: sampled-threshold depth-2 SAT vs brute force =="
"$EIG" tests/test_thr2.eigs || exit 1

echo "== rung 6: per-stage YBT conversion vs oracles =="
"$EIG" tests/test_ybt.eigs || exit 1

echo "== rung 7: Chen–Tal–Wang toolbox vs oracles =="
"$EIG" tests/test_ctw.eigs || exit 1

echo "== audits: JC audit case self-verification =="
python3 audits/verify_jc.py || exit 1

echo "== CLI demos (self-checking) =="
"$EIG" polymethod.eigs 12 60 1 || exit 1
"$EIG" polymethod.eigs max2sat 12 36 1 || exit 1
"$EIG" polymethod.eigs ac0 14 28 3 1 || exit 1

echo "polymethod gate: all green"
