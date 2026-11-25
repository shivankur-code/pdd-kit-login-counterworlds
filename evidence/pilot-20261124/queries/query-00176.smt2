; benchmark generated from python API
(set-info :status unknown)
(declare-fun left () Int)
(declare-fun right () Int)
(assert
 (let (($x35 (or (and (distinct right (ite (<= left right) left right)) true) (and (distinct right left) true))))
(and true $x35)))
(check-sat)
