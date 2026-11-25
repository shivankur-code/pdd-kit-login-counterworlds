; benchmark generated from python API
(set-info :status unknown)
(declare-fun right () Int)
(declare-fun left () Int)
(assert
 (let (($x35 (or (and (distinct right (ite (<= left right) left right)) true) (and (distinct right right) true))))
(and true $x35)))
(check-sat)
