; benchmark generated from python API
(set-info :status unknown)
(declare-fun balance () Int)
(declare-fun amount () Int)
(assert
 (let ((?x41 (ite true balance balance)))
(let (($x58 (and (= true (and (> amount 0) (<= amount balance))) (and (>= ?x41 0) (<= ?x41 balance)))))
(let (($x22 (not (and $x58 (= ?x41 (ite true (- balance amount) balance))))))
(let (($x8 (>= balance 0)))
(and $x8 $x22))))))
(check-sat)
