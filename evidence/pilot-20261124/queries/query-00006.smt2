; benchmark generated from python API
(set-info :status unknown)
(declare-fun balance () Int)
(declare-fun amount () Int)
(assert
 (let (($x11 (and (> amount 0) (<= amount balance))))
(let ((?x30 (ite $x11 0 balance)))
(let (($x42 (and (= $x11 $x11) (and (>= ?x30 0) (<= ?x30 balance)))))
(let (($x8 (>= balance 0)))
(and $x8 (not (and $x42 (= ?x30 (ite $x11 (- balance amount) balance))))))))))
(check-sat)
