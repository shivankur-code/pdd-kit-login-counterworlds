; benchmark generated from python API
(set-info :status unknown)
(declare-fun amount () Int)
(declare-fun balance () Int)
(declare-fun recipient () Int)
(assert
 (let (($x32 (>= recipient 0)))
(let (($x9 (> amount 0)))
(let (($x38 (and (>= balance amount) $x9 $x32)))
(and $x38 (not (= (- balance amount) (- balance amount))))))))
(check-sat)
