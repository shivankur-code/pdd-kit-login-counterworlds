; benchmark generated from python API
(set-info :status unknown)
(declare-fun balance () Int)
(declare-fun amount () Int)
(assert
 (let (($x17 (and (>= (ite true 0 balance) 0) (<= (ite true 0 balance) balance))))
(let (($x22 (and (= true (and (> amount 0) (<= amount balance))) $x17)))
(let (($x8 (>= balance 0)))
(and $x8 (not $x22))))))
(check-sat)
