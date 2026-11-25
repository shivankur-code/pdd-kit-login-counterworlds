; benchmark generated from python API
(set-info :status unknown)
(declare-fun balance () Int)
(declare-fun amount () Int)
(assert
 (let (($x8 (>= balance 0)))
(and $x8 (not (= false (and (> amount 0) (<= amount balance)))))))
(check-sat)
