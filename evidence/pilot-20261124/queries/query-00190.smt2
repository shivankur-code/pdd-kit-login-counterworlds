; benchmark generated from python API
(set-info :status unknown)
(declare-fun right () Int)
(declare-fun left () Int)
(assert
 (let (($x37 (<= left right)))
(let ((?x76 (ite $x37 left right)))
(and true (or (and (distinct ?x76 ?x76) true) (and (distinct right ?x76) true))))))
(check-sat)
