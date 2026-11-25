; benchmark generated from python API
(set-info :status unknown)
(declare-fun locked () Bool)
(declare-fun password () Bool)
(declare-fun exists () Bool)
(declare-fun account () Int)
(assert
 (let (($x9 (and exists password (not locked))))
(let (($x15 (= $x9 $x9)))
(let (($x37 (> account 0)))
(and $x37 (not $x15))))))
(check-sat)
