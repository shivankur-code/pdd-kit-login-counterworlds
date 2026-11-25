; benchmark generated from python API
(set-info :status unknown)
(declare-fun left () Int)
(declare-fun right () Int)
(assert
 (let (($x191 (and (>= right (ite (<= left right) left right)) (<= right (ite (<= left right) right left)))))
(let (($x37 (<= left right)))
(let ((?x17 (ite $x37 right left)))
(let (($x197 (and (<= ?x17 right) (and (and (>= ?x17 (ite $x37 left right)) (<= ?x17 ?x17)) $x191))))
(and true (not $x197)))))))
(check-sat)
