; benchmark generated from python API
(set-info :status unknown)
(declare-fun amount () Int)
(declare-fun recipient () Int)
(declare-fun balance () Int)
(assert
 (let (($x56 (or (and (distinct (- balance amount) (- balance amount)) true) (and (distinct (+ recipient amount) (+ (+ recipient amount) 1)) true))))
(let (($x32 (>= recipient 0)))
(let (($x38 (and (>= balance amount) (> amount 0) $x32)))
(and $x38 $x56)))))
(check-sat)
