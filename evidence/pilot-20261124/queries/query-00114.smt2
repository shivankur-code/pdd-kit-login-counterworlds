; benchmark generated from python API
(set-info :status unknown)
(declare-fun locked () Bool)
(declare-fun password () Bool)
(declare-fun exists () Bool)
(declare-fun account () Int)
(assert
 (let (($x37 (> account 0)))
(and $x37 (not (= false (and exists password (not locked)))))))
(check-sat)
