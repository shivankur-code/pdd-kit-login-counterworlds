; benchmark generated from python API
(set-info :status unknown)
(declare-fun admin () Bool)
(declare-fun account () Int)
(assert
 (let (($x37 (> account 0)))
(and $x37 (not (= false (and false admin))))))
(check-sat)
