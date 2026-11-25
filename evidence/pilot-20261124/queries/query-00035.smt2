; benchmark generated from python API
(set-info :status unknown)
(declare-fun balance () Int)
(declare-fun amount () Int)
(assert
 (let (($x11 (and (> amount 0) (<= amount balance))))
(let (($x82 (= $x11 $x11)))
(let (($x8 (>= balance 0)))
(and $x8 (not $x82))))))
(check-sat)
