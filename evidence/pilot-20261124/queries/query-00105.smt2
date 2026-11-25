; benchmark generated from python API
(set-info :status unknown)
(declare-fun account () Int)
(declare-fun admin () Bool)
(declare-fun locked () Bool)
(declare-fun password () Bool)
(declare-fun exists () Bool)
(assert
 (let (($x63 (=> false (= (ite false (ite admin account 0) (- 1)) account))))
(let (($x43 (and (= false (and exists password (not locked))) (= (and false admin) (and false admin)))))
(let (($x37 (> account 0)))
(and $x37 (not (and $x43 $x63)))))))
(check-sat)
