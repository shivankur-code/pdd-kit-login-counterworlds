; benchmark generated from python API
(set-info :status unknown)
(declare-fun balance () Int)
(assert
 (let (($x8 (>= balance 0)))
(and $x8 (not (and $x8 (<= balance balance))))))
(check-sat)
