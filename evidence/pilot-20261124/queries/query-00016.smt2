; benchmark generated from python API
(set-info :status unknown)
(declare-fun balance () Int)
(declare-fun amount () Int)
(assert
 (let (($x9 (> amount 0)))
(let (($x14 (and $x9 (< amount balance))))
(let ((?x67 (ite $x14 (- balance (* 2 amount)) balance)))
(let (($x117 (and (= $x14 (and $x9 (<= amount balance))) (and (>= ?x67 0) (<= ?x67 balance)))))
(let (($x8 (>= balance 0)))
(and $x8 (not (and $x117 (= ?x67 (ite $x14 (- balance amount) balance)))))))))))
(check-sat)
