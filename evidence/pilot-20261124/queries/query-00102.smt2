; benchmark generated from python API
(set-info :status unknown)
(declare-fun admin () Bool)
(declare-fun locked () Bool)
(declare-fun password () Bool)
(declare-fun exists () Bool)
(declare-fun account () Int)
(assert
 (let (($x43 (and (= false (and exists password (not locked))) (= (and false admin) (and false admin)))))
(let (($x37 (> account 0)))
(and $x37 (not $x43)))))
(check-sat)
