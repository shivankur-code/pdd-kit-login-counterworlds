; benchmark generated from python API
(set-info :status unknown)
(declare-fun balance () Int)
(declare-fun amount () Int)
(assert
 (let ((?x32 (ite true 0 balance)))
(let (($x22 (and (= true (and (> amount 0) (<= amount balance))) (and (>= ?x32 0) (<= ?x32 balance)))))
(let (($x72 (not (and $x22 (= ?x32 (ite true (- balance amount) balance))))))
(let (($x8 (>= balance 0)))
(and $x8 $x72))))))
(check-sat)
