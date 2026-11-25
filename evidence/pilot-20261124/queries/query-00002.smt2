; benchmark generated from python API
(set-info :status unknown)
(declare-fun balance () Int)
(declare-fun amount () Int)
(assert
 (let (($x11 (and (> amount 0) (<= amount balance))))
(let ((?x16 (ite $x11 (- balance amount) balance)))
(let (($x19 (and (= $x11 $x11) (and (>= ?x16 0) (<= ?x16 balance)))))
(let (($x8 (>= balance 0)))
(and $x8 (not (and $x19 (= ?x16 ?x16)))))))))
(check-sat)
