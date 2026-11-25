; benchmark generated from python API
(set-info :status unknown)
(declare-fun amount () Int)
(declare-fun recipient () Int)
(declare-fun balance () Int)
(assert
 (let (($x67 (and (= (- (- balance amount) 1) (- balance amount)) (>= (+ recipient amount) recipient))))
(let (($x32 (>= recipient 0)))
(let (($x9 (> amount 0)))
(let (($x38 (and (>= balance amount) $x9 $x32)))
(and $x38 (not (and $x67 (= (+ recipient amount) (+ recipient amount))))))))))
(check-sat)
