; benchmark generated from python API
(set-info :status unknown)
(declare-fun amount () Int)
(declare-fun recipient () Int)
(declare-fun balance () Int)
(assert
 (let ((?x17 (+ (+ recipient amount) 1)))
(let ((?x10 (* 2 amount)))
(let ((?x11 (+ recipient ?x10)))
(let (($x35 (or (and (distinct (- balance amount) (- balance amount)) true) (and (distinct ?x11 ?x17) true))))
(let (($x32 (>= recipient 0)))
(let (($x38 (and (>= balance amount) (> amount 0) $x32)))
(and $x38 $x35))))))))
(check-sat)
