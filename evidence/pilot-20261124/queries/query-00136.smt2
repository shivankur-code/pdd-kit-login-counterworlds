; benchmark generated from python API
(set-info :status unknown)
(declare-fun left () Int)
(declare-fun right () Int)
(assert
 (let (($x37 (<= left right)))
(let ((?x17 (ite $x37 right left)))
(let ((?x76 (ite $x37 left right)))
(let (($x168 (and (and (>= right ?x76) (<= right ?x17)) (and (>= ?x76 ?x76) (<= ?x76 ?x17)))))
(let (($x128 (and (<= right ?x76) $x168)))
(and true (not $x128))))))))
(check-sat)
