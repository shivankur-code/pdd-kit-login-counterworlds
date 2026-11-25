; benchmark generated from python API
(set-info :status unknown)
(declare-fun left () Int)
(declare-fun right () Int)
(assert
 (let (($x37 (<= left right)))
(let ((?x17 (ite $x37 right left)))
(let ((?x76 (ite $x37 left right)))
(let ((?x50 (- ?x76 1)))
(let (($x155 (<= ?x50 ?x17)))
(and true (not $x155))))))))
(check-sat)
