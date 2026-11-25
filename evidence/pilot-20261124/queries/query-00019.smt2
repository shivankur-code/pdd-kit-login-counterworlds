; benchmark generated from python API
(set-info :status unknown)
(declare-fun balance () Int)
(declare-fun amount () Int)
(assert
 (let (($x27 (and (>= (ite false balance balance) 0) (<= (ite false balance balance) balance))))
(let (($x39 (and (= false (and (> amount 0) (<= amount balance))) $x27)))
(let (($x8 (>= balance 0)))
(and $x8 (not $x39))))))
(check-sat)
