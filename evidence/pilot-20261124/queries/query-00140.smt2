; benchmark generated from python API
(set-info :status unknown)
(declare-fun left () Int)
(declare-fun right () Int)
(assert
 (let (($x135 (and (>= left (ite (<= left right) left right)) (<= left (ite (<= left right) right left)))))
(let (($x37 (<= left right)))
(let ((?x17 (ite $x37 right left)))
(let ((?x76 (ite $x37 left right)))
(let (($x202 (and (<= ?x76 left) (and (and (>= ?x76 ?x76) (<= ?x76 ?x17)) $x135))))
(and true (not $x202))))))))
(check-sat)
