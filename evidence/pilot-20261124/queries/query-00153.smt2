; benchmark generated from python API
(set-info :status unknown)
(declare-fun left () Int)
(declare-fun right () Int)
(assert
 (let (($x33 (and (= (ite (<= left right) right left) right) (= (ite (<= left right) left right) left))))
(let (($x61 (and (= (ite (<= left right) right left) left) (= (ite (<= left right) left right) right))))
(let (($x37 (<= left right)))
(let ((?x17 (ite $x37 right left)))
(let ((?x76 (ite $x37 left right)))
(let (($x98 (and (and (>= ?x17 ?x76) (<= ?x17 ?x17)) (and (>= ?x76 ?x76) (<= ?x76 ?x17)))))
(let (($x42 (and (<= ?x17 ?x76) $x98)))
(and true (not (and $x42 (or $x61 $x33))))))))))))
(check-sat)
