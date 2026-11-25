; benchmark generated from python API
(set-info :status unknown)
(declare-fun left () Int)
(declare-fun right () Int)
(assert
 (let (($x28 (and (= (ite (<= left right) left right) right) (= (ite (<= left right) right left) left))))
(let (($x32 (and (= (ite (<= left right) left right) left) (= (ite (<= left right) right left) right))))
(let (($x37 (<= left right)))
(let ((?x17 (ite $x37 right left)))
(let ((?x76 (ite $x37 left right)))
(let (($x95 (<= ?x76 ?x17)))
(let (($x92 (and $x95 (and (and (>= ?x76 ?x76) $x95) (and (>= ?x17 ?x76) (<= ?x17 ?x17))))))
(and true (not (and $x92 (or $x32 $x28))))))))))))
(check-sat)
