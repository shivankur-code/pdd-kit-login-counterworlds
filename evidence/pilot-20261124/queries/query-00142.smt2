; benchmark generated from python API
(set-info :status unknown)
(declare-fun left () Int)
(declare-fun right () Int)
(assert
 (let (($x13 (and (>= right (ite (<= left right) left right)) (<= right (ite (<= left right) right left)))))
(let (($x37 (<= left right)))
(let ((?x17 (ite $x37 right left)))
(let ((?x76 (ite $x37 left right)))
(let (($x194 (and (<= ?x76 right) (and (and (>= ?x76 ?x76) (<= ?x76 ?x17)) $x13))))
(and true (not $x194))))))))
(check-sat)
