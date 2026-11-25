; benchmark generated from python API
(set-info :status unknown)
(declare-fun balance () Int)
(declare-fun amount () Int)
(assert
 (let ((?x29 (ite false balance balance)))
(let (($x39 (and (= false (and (> amount 0) (<= amount balance))) (and (>= ?x29 0) (<= ?x29 balance)))))
(let (($x71 (not (and $x39 (= ?x29 (ite false (- balance amount) balance))))))
(let (($x8 (>= balance 0)))
(and $x8 $x71))))))
(check-sat)
