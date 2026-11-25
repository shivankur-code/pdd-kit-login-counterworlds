; benchmark generated from python API
(set-info :status unknown)
(declare-fun left () Int)
(declare-fun right () Int)
(assert
 (let (($x37 (<= left right)))
(let ((?x17 (ite $x37 right left)))
(let (($x33 (and (and (>= right (ite $x37 left right)) (<= right ?x17)) (and (>= ?x17 (ite $x37 left right)) (<= ?x17 ?x17)))))
(let (($x67 (<= right ?x17)))
(let (($x166 (and $x67 $x33)))
(and true (not $x166))))))))
(check-sat)
