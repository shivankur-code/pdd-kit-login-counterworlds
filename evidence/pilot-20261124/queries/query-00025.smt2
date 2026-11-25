; benchmark generated from python API
(set-info :status unknown)
(declare-fun balance () Int)
(declare-fun amount () Int)
(assert
 (let (($x37 (and (>= (ite true (- balance amount) balance) 0) (<= (ite true (- balance amount) balance) balance))))
(let (($x27 (and (= true (and (> amount 0) (<= amount balance))) $x37)))
(let (($x8 (>= balance 0)))
(and $x8 (not $x27))))))
(check-sat)
