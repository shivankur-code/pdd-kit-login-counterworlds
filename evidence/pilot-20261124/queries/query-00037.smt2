; benchmark generated from python API
(set-info :status unknown)
(declare-fun balance () Int)
(declare-fun amount () Int)
(assert
 (let (($x11 (and (> amount 0) (<= amount balance))))
(let ((?x54 (ite $x11 balance balance)))
(let ((?x32 (ite $x11 (- balance amount) balance)))
(let (($x8 (>= balance 0)))
(and $x8 (or (and (distinct $x11 $x11) true) (and (distinct ?x32 ?x54) true))))))))
(check-sat)
