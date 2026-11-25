; benchmark generated from python API
(set-info :status unknown)
(declare-fun left () Int)
(declare-fun right () Int)
(assert
 (let (($x26 (and (>= right (ite (<= left right) left right)) (<= right (ite (<= left right) right left)))))
(let (($x88 (and (>= left (ite (<= left right) left right)) (<= left (ite (<= left right) right left)))))
(let (($x37 (<= left right)))
(let (($x113 (and $x37 (and $x88 $x26))))
(and true (not $x113)))))))
(check-sat)
