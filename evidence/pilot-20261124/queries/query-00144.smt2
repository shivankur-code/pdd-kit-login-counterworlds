; benchmark generated from python API
(set-info :status unknown)
(declare-fun left () Int)
(declare-fun right () Int)
(assert
 (let (($x37 (<= left right)))
(let ((?x76 (ite $x37 left right)))
(let (($x140 (and (>= ?x76 ?x76) (<= ?x76 (ite $x37 right left)))))
(let (($x49 (and (<= ?x76 ?x76) (and $x140 $x140))))
(and true (not $x49)))))))
(check-sat)
