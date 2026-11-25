; benchmark generated from python API
(set-info :status unknown)
(declare-fun right () Int)
(declare-fun left () Int)
(assert
 (let (($x37 (<= left right)))
(let ((?x76 (ite $x37 left right)))
(let ((?x17 (ite $x37 right left)))
(let (($x122 (<= ?x17 ?x76)))
(and true (not $x122)))))))
(check-sat)
