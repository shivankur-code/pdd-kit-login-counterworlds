; benchmark generated from python API
(set-info :status unknown)
(declare-fun left () Int)
(declare-fun right () Int)
(assert
 (let (($x35 (or (and (distinct left right) true) (and (distinct left (ite (<= left right) right left)) true))))
(and true $x35)))
(check-sat)
