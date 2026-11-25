; benchmark generated from python API
(set-info :status unknown)
(declare-fun balance () Int)
(declare-fun amount () Int)
(assert
 (let (($x50 (and (>= (ite true (- balance (* 2 amount)) balance) 0) (<= (ite true (- balance (* 2 amount)) balance) balance))))
(let (($x49 (and (= true (and (> amount 0) (<= amount balance))) $x50)))
(let (($x8 (>= balance 0)))
(and $x8 (not $x49))))))
(check-sat)
