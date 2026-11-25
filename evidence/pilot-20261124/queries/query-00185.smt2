; benchmark generated from python API
(set-info :status unknown)
(declare-fun left () Int)
(declare-fun right () Int)
(assert
 (let (($x37 (<= left right)))
(let ((?x17 (ite $x37 right left)))
(and true (or (and (distinct right ?x17) true) (and (distinct ?x17 ?x17) true))))))
(check-sat)
