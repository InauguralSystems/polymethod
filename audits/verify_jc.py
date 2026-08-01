#!/usr/bin/env python3
"""Mechanical verification of audits/jc_audit.smt2's two claims, with no
dependency on the source paper: (1) det DF is the constant -2, (2) the map has
an explicit rational collision, so the file's correct answer is sat.

Exact rational arithmetic throughout (fractions.Fraction + forward-mode dual
numbers); no external packages. det DF is a polynomial of total degree <= 18,
so agreeing with -2 at N random rational points leaves a nonconstant
determinant probability ~0 (Schwartz-Zippel over a large sample space); the
collision check is exact, full stop.

The checker is itself checked: a planted fault (a perturbed f3 whose Jacobian
is NOT constant) must be caught, or the verifier exits nonzero.
"""
import random
import sys
from fractions import Fraction as Fr


class D:
    """Dual number: exact value + exact 3-gradient (forward-mode AD)."""

    def __init__(self, v, g):
        self.v, self.g = v, tuple(g)

    def __add__(self, o):
        o = lift(o)
        return D(self.v + o.v, [a + b for a, b in zip(self.g, o.g)])

    __radd__ = __add__

    def __sub__(self, o):
        o = lift(o)
        return D(self.v - o.v, [a - b for a, b in zip(self.g, o.g)])

    def __rsub__(self, o):
        return lift(o).__sub__(self)

    def __mul__(self, o):
        o = lift(o)
        return D(self.v * o.v, [self.v * b + o.v * a for a, b in zip(self.g, o.g)])

    __rmul__ = __mul__

    def __pow__(self, n):
        r = lift(1)
        for _ in range(n):
            r = r * self
        return r


def lift(x):
    return x if isinstance(x, D) else D(Fr(x), [Fr(0)] * 3)


def F(u, v, w, fault=False):
    f1 = (1 + u * v) ** 3 * w + v ** 2 * (1 + u * v) * (4 + 3 * u * v)
    f2 = v + 3 * u * (1 + u * v) ** 2 * w + 3 * u * v ** 2 * (4 + 3 * u * v)
    f3 = 2 * u - 3 * u ** 2 * v - u ** 3 * w
    if fault:  # planted fault: breaks Jacobian constancy, must be caught
        f3 = f3 + u * v * w
    return f1, f2, f3


def det_DF(p, fault=False):
    basis = [D(Fr(p[i]), [Fr(int(j == i)) for j in range(3)]) for i in range(3)]
    m = [f.g for f in F(*basis, fault=fault)]
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))


def value(p):
    return tuple(f.v for f in F(*(lift(Fr(x)) for x in p)))


def main():
    rng = random.Random(7)
    pts = [tuple(Fr(rng.randint(-999, 999), rng.randint(1, 97)) for _ in range(3))
           for _ in range(20)]

    dets = {det_DF(p) for p in pts}
    assert dets == {Fr(-2)}, f"det DF not the constant -2: {dets}"

    p, q = (1, 0, 2), (0, 6, -142)
    assert value(p) == value(q) == (Fr(2), Fr(6), Fr(0)), \
        f"collision witness failed: {value(p)} vs {value(q)}"
    assert p != q

    faulted = {det_DF(pt, fault=True) for pt in pts}
    assert len(faulted) > 1, "planted fault NOT caught — the checker is broken"

    print("ok: det DF = -2 (constant, 20 random rational points)")
    print("ok: F(1,0,2) = F(0,6,-142) = (2, 6, 0) — explicit rational collision")
    print("ok: planted nonconstant-Jacobian fault caught")
    print("jc_audit.smt2 correct answer: sat")


if __name__ == "__main__":
    sys.exit(main())
