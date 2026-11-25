; benchmark generated from python API
(set-info :status unknown)
(declare-fun account () Int)
(declare-fun admin () Bool)
(declare-fun locked () Bool)
(declare-fun password () Bool)
(declare-fun exists () Bool)
(assert
 (let (($x32 (=> true (= (ite true (ite admin account 0) (- 1)) account))))
(let (($x67 (and (= true (and exists password (not locked))) (= (and true admin) (and true admin)))))
(let (($x37 (> account 0)))
(and $x37 (not (and $x67 $x32)))))))
(check-sat)
