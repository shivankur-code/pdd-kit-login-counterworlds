; benchmark generated from python API
(set-info :status unknown)
(declare-fun balance () Int)
(declare-fun amount () Int)
(assert
 (let (($x98 (and (>= (ite false 0 balance) 0) (<= (ite false 0 balance) balance))))
(let (($x71 (and (= false (and (> amount 0) (<= amount balance))) $x98)))
(let (($x8 (>= balance 0)))
(and $x8 (not $x71))))))
(check-sat)
