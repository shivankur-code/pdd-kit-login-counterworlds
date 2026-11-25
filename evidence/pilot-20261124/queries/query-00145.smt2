; benchmark generated from python API
(set-info :status unknown)
(declare-fun left () Int)
(declare-fun right () Int)
(assert
 (let (($x37 (<= left right)))
(let ((?x76 (ite $x37 left right)))
(let (($x43 (= ?x76 left)))
(let (($x202 (= ?x76 right)))
(let (($x140 (and (>= ?x76 ?x76) (<= ?x76 (ite $x37 right left)))))
(let (($x49 (and (<= ?x76 ?x76) (and $x140 $x140))))
(and true (not (and $x49 (or (and $x43 $x202) (and $x202 $x43))))))))))))
(check-sat)
