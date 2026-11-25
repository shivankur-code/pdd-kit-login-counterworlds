; benchmark generated from python API
(set-info :status unknown)
(declare-fun left () Int)
(declare-fun right () Int)
(assert
 (let (($x170 (and (>= left (ite (<= left right) left right)) (<= left (ite (<= left right) right left)))))
(let (($x37 (<= left right)))
(let ((?x17 (ite $x37 right left)))
(let (($x186 (and (<= ?x17 left) (and (and (>= ?x17 (ite $x37 left right)) (<= ?x17 ?x17)) $x170))))
(and true (not $x186)))))))
(check-sat)
