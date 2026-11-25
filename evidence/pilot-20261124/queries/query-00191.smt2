; benchmark generated from python API
(set-info :status unknown)
(declare-fun left () Int)
(declare-fun right () Int)
(assert
 (let (($x37 (<= left right)))
(let ((?x76 (ite $x37 left right)))
(and true (or (and (distinct ?x76 ?x76) true) (and (distinct right (ite $x37 right left)) true))))))
(check-sat)
