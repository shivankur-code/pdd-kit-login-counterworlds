; benchmark generated from python API
(set-info :status unknown)
(declare-fun amount () Int)
(declare-fun recipient () Int)
(declare-fun balance () Int)
(assert
 (let (($x47 (and (= (- balance amount) (- balance amount)) (>= (+ (+ recipient amount) 1) recipient))))
(let (($x17 (and $x47 (= (+ (+ recipient amount) 1) (+ recipient amount)))))
(let (($x32 (>= recipient 0)))
(let (($x9 (> amount 0)))
(let (($x38 (and (>= balance amount) $x9 $x32)))
(and $x38 (not $x17))))))))
(check-sat)
