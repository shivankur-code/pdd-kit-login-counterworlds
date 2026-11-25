; benchmark generated from python API
(set-info :status unknown)
(declare-fun right () Int)
(declare-fun left () Int)
(assert
 (and true (or (and (distinct left right) true) (and (distinct left right) true))))
(check-sat)
