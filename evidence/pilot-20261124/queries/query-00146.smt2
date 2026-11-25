; benchmark generated from python API
(set-info :status unknown)
(declare-fun left () Int)
(declare-fun right () Int)
(assert
 (let (($x37 (<= left right)))
(let ((?x17 (ite $x37 right left)))
(let ((?x76 (ite $x37 left right)))
(let (($x95 (<= ?x76 ?x17)))
(let (($x92 (and $x95 (and (and (>= ?x76 ?x76) $x95) (and (>= ?x17 ?x76) (<= ?x17 ?x17))))))
(and true (not $x92))))))))
(check-sat)
