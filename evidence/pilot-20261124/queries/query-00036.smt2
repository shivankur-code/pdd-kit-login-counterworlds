; benchmark generated from python API
(set-info :status unknown)
(declare-fun balance () Int)
(assert
 (let (($x14 (and (>= (+ balance 1) 0) (<= (+ balance 1) balance))))
(let (($x8 (>= balance 0)))
(and $x8 (not $x14)))))
(check-sat)
