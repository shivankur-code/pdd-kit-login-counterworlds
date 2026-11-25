; benchmark generated from python API
(set-info :status unknown)
(declare-fun left () Int)
(declare-fun right () Int)
(assert
 (let (($x20 (or (and (= right left) (= left right)) (and (= right right) (= left left)))))
(let (($x88 (and (>= left (ite (<= left right) left right)) (<= left (ite (<= left right) right left)))))
(let (($x115 (and (>= right (ite (<= left right) left right)) (<= right (ite (<= left right) right left)))))
(let (($x136 (and (<= right left) (and $x115 $x88))))
(and true (not (and $x136 $x20))))))))
(check-sat)
