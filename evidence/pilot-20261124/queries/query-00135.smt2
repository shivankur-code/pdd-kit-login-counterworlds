; benchmark generated from python API
(set-info :status unknown)
(declare-fun left () Int)
(declare-fun right () Int)
(assert
 (let (($x168 (or (and (= right left) (= right right)) (and (= right right) (= right left)))))
(let (($x115 (and (>= right (ite (<= left right) left right)) (<= right (ite (<= left right) right left)))))
(let (($x26 (and (<= right right) (and $x115 $x115))))
(and true (not (and $x26 $x168)))))))
(check-sat)
