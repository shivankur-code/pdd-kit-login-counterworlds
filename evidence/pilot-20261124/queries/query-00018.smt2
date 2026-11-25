; benchmark generated from python API
(set-info :status unknown)
(declare-fun balance () Int)
(declare-fun amount () Int)
(assert
 (let ((?x23 (ite false (- balance amount) balance)))
(let (($x17 (and (= false (and (> amount 0) (<= amount balance))) (and (>= ?x23 0) (<= ?x23 balance)))))
(let (($x8 (>= balance 0)))
(and $x8 (not (and $x17 (= ?x23 ?x23))))))))
(check-sat)
