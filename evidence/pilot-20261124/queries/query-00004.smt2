; benchmark generated from python API
(set-info :status unknown)
(declare-fun balance () Int)
(declare-fun amount () Int)
(assert
 (let (($x11 (and (> amount 0) (<= amount balance))))
(let ((?x34 (ite $x11 balance balance)))
(let (($x58 (and (= $x11 $x11) (and (>= ?x34 0) (<= ?x34 balance)))))
(let (($x8 (>= balance 0)))
(and $x8 (not (and $x58 (= ?x34 (ite $x11 (- balance amount) balance))))))))))
(check-sat)
