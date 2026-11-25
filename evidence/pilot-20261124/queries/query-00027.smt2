; benchmark generated from python API
(set-info :status unknown)
(declare-fun balance () Int)
(declare-fun amount () Int)
(assert
 (let (($x94 (and (>= (ite true balance balance) 0) (<= (ite true balance balance) balance))))
(let (($x58 (and (= true (and (> amount 0) (<= amount balance))) $x94)))
(let (($x8 (>= balance 0)))
(and $x8 (not $x58))))))
(check-sat)
