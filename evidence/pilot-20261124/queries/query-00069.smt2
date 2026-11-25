; benchmark generated from python API
(set-info :status unknown)
(declare-fun amount () Int)
(declare-fun recipient () Int)
(declare-fun balance () Int)
(assert
 (let (($x141 (and (= 0 (- balance amount)) (>= (+ recipient (* 2 amount)) recipient))))
(let (($x58 (and $x141 (= (+ recipient (* 2 amount)) (+ recipient amount)))))
(let (($x32 (>= recipient 0)))
(let (($x9 (> amount 0)))
(let (($x38 (and (>= balance amount) $x9 $x32)))
(and $x38 (not $x58))))))))
(check-sat)
