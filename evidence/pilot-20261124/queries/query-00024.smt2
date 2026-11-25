; benchmark generated from python API
(set-info :status unknown)
(declare-fun balance () Int)
(declare-fun amount () Int)
(assert
 (let ((?x14 (ite false (- balance (* 2 amount)) balance)))
(let (($x107 (and (= false (and (> amount 0) (<= amount balance))) (and (>= ?x14 0) (<= ?x14 balance)))))
(let (($x31 (not (and $x107 (= ?x14 (ite false (- balance amount) balance))))))
(let (($x8 (>= balance 0)))
(and $x8 $x31))))))
(check-sat)
