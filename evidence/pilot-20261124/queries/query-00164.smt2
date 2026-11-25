; benchmark generated from python API
(set-info :status unknown)
(declare-fun right () Int)
(declare-fun left () Int)
(assert
 (let (($x35 (or (and (distinct left (ite (<= left right) left right)) true) (and (distinct left right) true))))
(and true $x35)))
(check-sat)
