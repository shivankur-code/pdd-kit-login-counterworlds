; benchmark generated from python API
(set-info :status unknown)
(declare-fun left () Int)
(declare-fun right () Int)
(assert
 (let (($x37 (<= left right)))
(let ((?x17 (ite $x37 right left)))
(let ((?x76 (ite $x37 left right)))
(let (($x143 (and (and (>= left ?x76) (<= left ?x17)) (and (>= ?x76 ?x76) (<= ?x76 ?x17)))))
(let (($x69 (and (<= left ?x76) $x143)))
(and true (not $x69))))))))
(check-sat)
