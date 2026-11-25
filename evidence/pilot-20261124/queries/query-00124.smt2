; benchmark generated from python API
(set-info :status unknown)
(declare-fun left () Int)
(declare-fun right () Int)
(assert
 (let (($x88 (and (>= left (ite (<= left right) left right)) (<= left (ite (<= left right) right left)))))
(let (($x59 (and (<= left left) (and $x88 $x88))))
(and true (not $x59)))))
(check-sat)
