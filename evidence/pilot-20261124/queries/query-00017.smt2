; benchmark generated from python API
(set-info :status unknown)
(declare-fun balance () Int)
(declare-fun amount () Int)
(assert
 (let (($x32 (and (>= (ite false (- balance amount) balance) 0) (<= (ite false (- balance amount) balance) balance))))
(let (($x17 (and (= false (and (> amount 0) (<= amount balance))) $x32)))
(let (($x8 (>= balance 0)))
(and $x8 (not $x17))))))
(check-sat)
