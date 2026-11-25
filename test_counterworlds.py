import unittest

import z3

import counterworlds as study


class ContractTests(unittest.TestCase):
    def status(self, task, property_builder):
        inputs = study.variables(task)
        solver = z3.Solver()
        solver.set(timeout=5000)
        solver.add(study.domain(task, inputs), z3.Not(property_builder(inputs)))
        return solver.check()

    def test_intended_implementations_satisfy_both_contracts(self):
        for task in study.TASKS:
            with self.subTest(task=task):
                def property_builder(inputs):
                    output = study.semantics(task, inputs, *study.intended(task))
                    return z3.And(*study.clauses(task, inputs, output), study.added_intent(task, inputs, output))
                self.assertEqual(self.status(task, property_builder), z3.unsat)

    def test_each_mutant_violates_only_targeted_clause(self):
        for task in study.TASKS:
            for target in range(2):
                for clause in range(2):
                    with self.subTest(task=task, target=target, clause=clause):
                        result = self.status(task, lambda inputs: study.clauses(task, inputs, study.mutant(task, inputs, target))[clause])
                        self.assertEqual(result, z3.sat if target == clause else z3.unsat)

    def test_denial_is_not_a_valid_weak_withdrawal(self):
        self.assertEqual(self.status("withdrawal", lambda inputs: z3.And(*study.clauses(
            "withdrawal", inputs, study.semantics("withdrawal", inputs, 2, 0)))), z3.sat)


if __name__ == "__main__":
    unittest.main()