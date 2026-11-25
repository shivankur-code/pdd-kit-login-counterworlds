; benchmark generated from python API
(set-info :status unknown)
(declare-fun balance () Int)
(declare-fun amount () Int)
(assert
 (let (($x11 (and (> amount 0) (<= amount balance))))
(let ((?x56 (ite $x11 0 balance)))
(let ((?x71 (ite $x11 balance balance)))
(let (($x8 (>= balance 0)))
(and $x8 (or (and (distinct $x11 $x11) true) (and (distinct ?x71 ?x56) true))))))))
(check-sat)
