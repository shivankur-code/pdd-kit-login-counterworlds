; benchmark generated from python API
(set-info :status unknown)
(declare-fun right () Int)
(declare-fun left () Int)
(assert
 (let ((?x74 (ite (< left right) left right)))
(let ((?x92 (+ left right)))
(let ((?x105 (- ?x92 ?x74)))
(let (($x10 (<= left right)))
(let ((?x69 (ite $x10 right left)))
(and true (or (and (distinct (ite $x10 left right) ?x74) true) (and (distinct ?x69 ?x105) true)))))))))
(check-sat)
