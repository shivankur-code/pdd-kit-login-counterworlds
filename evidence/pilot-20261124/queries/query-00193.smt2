; benchmark generated from python API
(set-info :status unknown)
(declare-fun left () Int)
(declare-fun right () Int)
(assert
 (let (($x37 (<= left right)))
(let ((?x17 (ite $x37 right left)))
(let ((?x76 (ite $x37 left right)))
(and true (or (and (distinct ?x76 ?x76) true) (and (distinct ?x76 ?x17) true)))))))
(check-sat)
