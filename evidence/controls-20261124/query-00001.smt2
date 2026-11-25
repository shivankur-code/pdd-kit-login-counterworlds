; benchmark generated from python API
(set-info :status unknown)
(declare-fun balance () Int)
(declare-fun amount () Int)
(assert
 (let (($x17 (not (or (<= amount 0) (> amount balance)))))
(let ((?x20 (ite $x17 (+ balance (- amount)) balance)))
(let (($x9 (<= amount balance)))
(let (($x10 (and (> amount 0) $x9)))
(let ((?x15 (ite $x10 (- balance amount) balance)))
(let (($x21 (>= balance 0)))
(and $x21 (or (and (distinct $x10 $x17) true) (and (distinct ?x15 ?x20) true))))))))))
(check-sat)
