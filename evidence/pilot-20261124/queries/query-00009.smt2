; benchmark generated from python API
(set-info :status unknown)
(declare-fun balance () Int)
(declare-fun amount () Int)
(assert
 (let (($x9 (> amount 0)))
(let (($x14 (and $x9 (< amount balance))))
(let ((?x23 (ite $x14 (- balance amount) balance)))
(let (($x21 (and (= $x14 (and $x9 (<= amount balance))) (and (>= ?x23 0) (<= ?x23 balance)))))
(let (($x8 (>= balance 0)))
(and $x8 (not $x21))))))))
(check-sat)
