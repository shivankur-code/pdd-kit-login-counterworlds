; benchmark generated from python API
(set-info :status unknown)
(declare-fun balance () Int)
(declare-fun amount () Int)
(assert
 (let (($x9 (> amount 0)))
(let (($x14 (and $x9 (< amount balance))))
(let ((?x43 (ite $x14 0 balance)))
(let (($x53 (and (= $x14 (and $x9 (<= amount balance))) (and (>= ?x43 0) (<= ?x43 balance)))))
(let (($x8 (>= balance 0)))
(and $x8 (not $x53))))))))
(check-sat)
