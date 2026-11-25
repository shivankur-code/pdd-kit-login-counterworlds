; benchmark generated from python API
(set-info :status unknown)
(declare-fun balance () Int)
(declare-fun amount () Int)
(assert
 (let (($x11 (and (> amount 0) (<= amount balance))))
(let ((?x19 (ite $x11 (- balance (* 2 amount)) balance)))
(let (($x40 (and (= $x11 $x11) (and (>= ?x19 0) (<= ?x19 balance)))))
(let (($x8 (>= balance 0)))
(and $x8 (not (and $x40 (= ?x19 (ite $x11 (- balance amount) balance))))))))))
(check-sat)
