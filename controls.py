import argparse
import json
from pathlib import Path

import z3

import counterworlds as study


def main(destination):
    destination.mkdir(parents=True, exist_ok=False)
    solver = study.EvidenceSolver(destination)
    results = []
    for task in study.TASKS:
        inputs = study.variables(task)
        baseline = study.semantics(task, inputs, *study.intended(task))
        if task == "withdrawal":
            allowed = z3.Not(z3.Or(inputs["amount"] <= 0, inputs["amount"] > inputs["balance"]))
            alternative = (allowed, z3.If(allowed, inputs["balance"] + (-inputs["amount"]), inputs["balance"]))
        elif task == "transfer":
            alternative = (inputs["balance"] + (-inputs["amount"]), inputs["amount"] + inputs["recipient"])
        elif task == "login":
            allowed = z3.Not(z3.Or(z3.Not(inputs["exists"]), z3.Not(inputs["password"]), inputs["locked"]))
            alternative = (allowed, z3.If(allowed, inputs["admin"], False), z3.If(allowed, inputs["account"], -1))
        else:
            minimum = z3.If(inputs["left"] < inputs["right"], inputs["left"], inputs["right"])
            alternative = (minimum, inputs["left"] + inputs["right"] - minimum)
        equivalence = solver.check(z3.And(study.domain(task, inputs), z3.Or(
            *[before != after for before, after in zip(baseline, alternative)])), inputs)
        outputs = []
        for side in ("first", "second"):
            outputs.append(tuple(z3.Bool(f"{side}_{index}") if z3.is_bool(value)
                                 else z3.Int(f"{side}_{index}") for index, value in enumerate(baseline)))
        witness_variables = dict(inputs)
        for side, values in zip(("first", "second"), outputs):
            witness_variables.update({f"{side}_{index}": value for index, value in enumerate(values)})
        different = z3.Or(*[before != after for before, after in zip(*outputs)])
        weak = z3.And(*[z3.And(*study.clauses(task, inputs, output)) for output in outputs])
        strong = z3.And(weak, *[study.added_intent(task, inputs, output) for output in outputs])
        weak_freedom = solver.check(z3.And(study.domain(task, inputs), weak, different), witness_variables)
        strong_unique = solver.check(z3.And(study.domain(task, inputs), strong, different), witness_variables)
        observations = [values[:2] + (z3.If(values[0], values[2], -1),) if task == "login" else values
                        for values in outputs]
        observable_difference = z3.Or(*[before != after for before, after in zip(*observations)])
        observable_unique = solver.check(z3.And(study.domain(task, inputs), strong, observable_difference), witness_variables)
        expected_full = "sat" if task == "login" else "unsat"
        if (equivalence["result"], weak_freedom["result"], strong_unique["result"], observable_unique["result"]) != ("unsat", "sat", expected_full, "unsat"):
            raise RuntimeError(f"Control failed: {task}")
        results.append({"task": task, "equivalent_rewrite": equivalence,
                        "weak_contract_output_freedom": weak_freedom,
                        "strong_contract_output_uniqueness": strong_unique,
                        "strong_contract_observable_uniqueness": observable_unique})
    payload = {"status": "PASS", "kind": "post-pilot-supplemental-controls",
               "scope": "Output uniqueness for mathematical contracts, not arbitrary program termination, side effects, or deployed code.",
               "source_sha256": {name: study.digest(study.ROOT / name) for name in
                                 ("counterworlds.py", "controls.py", "audit.py", "test_counterworlds.py", "PLAN.md")},
               "controls": results}
    (destination / "controls.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    main(parser.parse_args().out)