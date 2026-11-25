; benchmark generated from python API
(set-info :status unknown)
(declare-fun left () Int)
(declare-fun right () Int)
(assert
 (let (($x37 (<= left right)))
(let ((?x17 (ite $x37 right left)))
(let (($x202 (<= ?x17 ?x17)))
(let (($x168 (and (>= ?x17 (ite $x37 left right)) $x202)))
(let (($x106 (and $x202 (and $x168 $x168))))
(and true (not $x106))))))))
(check-sat)
