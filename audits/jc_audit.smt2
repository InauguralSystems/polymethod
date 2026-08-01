; Jacobian-conjecture audit case (Alpöge 2026, dim 3, degree 7, det DF = -2).
; A tool that infers GLOBAL injectivity from a constant/nonvanishing Jacobian
; will answer unsat here. The correct answer is sat.
;
; Both claims are mechanically verified by audits/verify_jc.py (exact rational
; arithmetic, no dependencies):
;   det DF = -2       (constant; checked at random rational points)
;   F(1, 0, 2) = F(0, 6, -142) = (2, 6, 0)   (an explicit rational collision)
; So "sat" does not rest on the paper: a satisfying assignment is
;   a=1, b=0, c=2, x=0, y=6, z=-142.
;
; Scope note: the counterexample is dim >= 3 only — the plane case remains open.
(set-logic QF_NRA)
(declare-const a Real) (declare-const b Real) (declare-const c Real)
(declare-const x Real) (declare-const y Real) (declare-const z Real)
(define-fun f1 ((u Real)(v Real)(w Real)) Real
  (+ (* (^ (+ 1 (* u v)) 3) w) (* (* v v) (+ 1 (* u v)) (+ 4 (* 3 u v)))))
(define-fun f2 ((u Real)(v Real)(w Real)) Real
  (+ v (* 3 u (^ (+ 1 (* u v)) 2) w) (* 3 u (* v v) (+ 4 (* 3 u v)))))
(define-fun f3 ((u Real)(v Real)(w Real)) Real
  (- (* 2 u) (* 3 u u v) (* u u u w)))
(assert (and (= (f1 a b c) (f1 x y z)) (= (f2 a b c) (f2 x y z)) (= (f3 a b c) (f3 x y z))))
(assert (or (distinct a x) (distinct b y) (distinct c z)))   ; two distinct preimages
(check-sat)
