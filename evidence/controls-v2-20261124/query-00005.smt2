; benchmark generated from python API
(set-info :status unknown)
(declare-fun recipient () Int)
(declare-fun amount () Int)
(declare-fun balance () Int)
(assert
 (let (($x105 (or (and (distinct (- balance amount) (+ balance (- amount))) true) (and (distinct (+ recipient amount) (+ amount recipient)) true))))
(let (($x8 (> amount 0)))
(and (and (>= balance amount) $x8 (>= recipient 0)) $x105))))
(check-sat)
