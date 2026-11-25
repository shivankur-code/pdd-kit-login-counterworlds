; benchmark generated from python API
(set-info :status unknown)
(declare-fun balance () Int)
(declare-fun amount () Int)
(assert
 (let (($x45 (and (>= (ite false (- balance (* 2 amount)) balance) 0) (<= (ite false (- balance (* 2 amount)) balance) balance))))
(let (($x107 (and (= false (and (> amount 0) (<= amount balance))) $x45)))
(let (($x8 (>= balance 0)))
(and $x8 (not $x107))))))
(check-sat)
