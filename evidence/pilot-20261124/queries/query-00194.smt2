; benchmark generated from python API
(set-info :status unknown)
(declare-fun left () Int)
(declare-fun right () Int)
(assert
 (let (($x37 (<= left right)))
(let ((?x17 (ite $x37 right left)))
(let ((?x76 (ite $x37 left right)))
(let (($x56 (and (distinct ?x76 ?x17) true)))
(and true (or $x56 $x56)))))))
(check-sat)
