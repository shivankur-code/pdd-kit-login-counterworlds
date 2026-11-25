; benchmark generated from python API
(set-info :status unknown)
(declare-fun balance () Int)
(declare-fun amount () Int)
(assert
 (let ((?x41 (* 2 amount)))
(let ((?x33 (- balance ?x41)))
(let ((?x15 (ite true ?x33 balance)))
(let (($x49 (and (= true (and (> amount 0) (<= amount balance))) (and (>= ?x15 0) (<= ?x15 balance)))))
(let (($x107 (not (and $x49 (= ?x15 (ite true (- balance amount) balance))))))
(let (($x8 (>= balance 0)))
(and $x8 $x107))))))))
(check-sat)
