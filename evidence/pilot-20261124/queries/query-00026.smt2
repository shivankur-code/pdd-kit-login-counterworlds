; benchmark generated from python API
(set-info :status unknown)
(declare-fun balance () Int)
(declare-fun amount () Int)
(assert
 (let ((?x23 (- balance amount)))
(let ((?x92 (ite true ?x23 balance)))
(let (($x27 (and (= true (and (> amount 0) (<= amount balance))) (and (>= ?x92 0) (<= ?x92 balance)))))
(let (($x8 (>= balance 0)))
(and $x8 (not (and $x27 (= ?x92 ?x92)))))))))
(check-sat)
