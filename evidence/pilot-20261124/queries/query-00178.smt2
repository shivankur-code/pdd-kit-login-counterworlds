; benchmark generated from python API
(set-info :status unknown)
(declare-fun right () Int)
(declare-fun left () Int)
(assert
 (let (($x37 (<= left right)))
(let ((?x76 (ite $x37 left right)))
(let (($x56 (and (distinct right ?x76) true)))
(and true (or $x56 $x56))))))
(check-sat)
