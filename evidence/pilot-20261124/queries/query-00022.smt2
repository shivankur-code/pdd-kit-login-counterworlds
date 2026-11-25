; benchmark generated from python API
(set-info :status unknown)
(declare-fun balance () Int)
(declare-fun amount () Int)
(assert
 (let ((?x92 (ite false 0 balance)))
(let (($x71 (and (= false (and (> amount 0) (<= amount balance))) (and (>= ?x92 0) (<= ?x92 balance)))))
(let (($x117 (not (and $x71 (= ?x92 (ite false (- balance amount) balance))))))
(let (($x8 (>= balance 0)))
(and $x8 $x117))))))
(check-sat)
