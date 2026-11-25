; benchmark generated from python API
(set-info :status unknown)
(declare-fun recipient () Int)
(declare-fun amount () Int)
(declare-fun balance () Int)
(assert
 (let (($x23 (and (= balance (- balance amount)) (>= (+ recipient (* 2 amount)) recipient))))
(let (($x32 (>= recipient 0)))
(let (($x9 (> amount 0)))
(let (($x38 (and (>= balance amount) $x9 $x32)))
(and $x38 (not $x23)))))))
(check-sat)
