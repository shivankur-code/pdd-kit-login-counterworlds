import argparse
import copy
import itertools
import json
import unittest
from pathlib import Path

import z3

from audit import direct, properties, require, sha


ROOT = Path(__file__).resolve().parent
PILOT = ROOT / "evidence/pilot-20261124"
CONTROLS = ROOT / "evidence/controls-v2-20261124"
TASKS = {"withdrawal", "transfer", "login", "sort"}


def legal(task, inputs):
    if task == "withdrawal":
        return inputs["balance"] >= 0
    if task == "transfer":
        return 0 < inputs["amount"] <= inputs["balance"] and inputs["recipient"] >= 0
    if task == "login":
        return inputs["account"] > 0
    return True


def validate_controls(payload, directory):
    require(len(payload["controls"]) == 4 and {panel["task"] for panel in payload["controls"]} == TASKS, "Invalid control roster")
    total = 0
    witnessed = 0
    for panel in payload["controls"]:
        task = panel["task"]
        expected = {"equivalent_rewrite": "unsat", "weak_contract_output_freedom": "sat",
                    "strong_contract_output_uniqueness": "sat" if task == "login" else "unsat",
                    "strong_contract_observable_uniqueness": "unsat"}
        for kind, status in expected.items():
            check = panel[kind]
            require(check["result"] == status, "Unexpected control status")
            solver = z3.Solver()
            solver.set(timeout=5000)
            solver.from_file(str(directory / check["query"]))
            require(str(solver.check()) == status, "Control query replay failed")
            total += 1
            witness = check["witness"]
            if status == "unsat":
                require(witness is None, "UNSAT has witness")
                continue
            require(witness is not None, "SAT missing witness")
            inputs = {key: value for key, value in witness.items() if not key.startswith(("first_", "second_"))}
            require(legal(task, inputs), "Illegal witness input")
            width = 3 if task == "login" else 2
            before, after = ([witness[f"{side}_{index}"] for index in range(width)] for side in ("first", "second"))
            require(before != after, "Witness does not distinguish outputs")
            for output in (before, after):
                clauses = properties(task, inputs, output)
                require(all(clauses[:2] if kind.startswith("weak") else clauses), "Witness fails its contract")
            witnessed += 1
    require(total == 16 and witnessed == 5, "Control accounting mismatch")
    return total, witnessed


class EvidenceTamperTests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads((CONTROLS / "controls.json").read_text(encoding="utf-8"))

    def test_valid_controls(self):
        self.assertEqual(validate_controls(self.payload, CONTROLS), (16, 5))

    def test_missing_task_rejected(self):
        self.payload["controls"].pop()
        with self.assertRaises(ValueError):
            validate_controls(self.payload, CONTROLS)

    def test_false_uniqueness_rejected(self):
        self.payload["controls"][2]["strong_contract_output_uniqueness"]["result"] = "unsat"
        with self.assertRaises(ValueError):
            validate_controls(self.payload, CONTROLS)

    def test_fabricated_witness_rejected(self):
        witness = self.payload["controls"][1]["weak_contract_output_freedom"]["witness"]
        witness["first_0"] = witness["balance"] + 100
        with self.assertRaises(ValueError):
            validate_controls(self.payload, CONTROLS)


def validate():
    report = json.loads((PILOT / "results.json").read_text(encoding="utf-8"))
    audit = json.loads((PILOT / "audit.json").read_text(encoding="utf-8"))
    require(audit["status"] == "PASS" and audit["results_sha256"] == sha(PILOT / "results.json"), "Audit binding failed")
    require(len(report["tasks"]) == 4 and {panel["task"] for panel in report["tasks"]} == TASKS, "Invalid task roster")
    for name, checksum in report["source_sha256"].items():
        require(sha(ROOT / name) == checksum, "Pilot source changed")
    all_queries = []
    examples = []
    isolated_mutants = 0
    for panel in report["tasks"]:
        task = panel["task"]
        expected_ids = set(itertools.product(range(4), repeat=2))
        require(len(panel["candidates"]) == 16 and {tuple(item["id"]) for item in panel["candidates"]} == expected_ids, "Invalid candidate roster")
        accepted = {tuple(item["id"]) for item in panel["candidates"] if item["weak"]["result"] == "unsat"}
        expected_pairs = set(itertools.combinations(sorted(accepted), 2))
        require(len(panel["pairs"]) == len(expected_pairs) and
                {(tuple(pair["left"]), tuple(pair["right"])) for pair in panel["pairs"]} == expected_pairs, "Invalid pair roster")
        for candidate in panel["candidates"]:
            all_queries.extend(candidate[kind]["query"] for kind in ("weak", "strong"))
        require(len(panel["mutations"]) == 2 and {item["target"] for item in panel["mutations"]} == {0, 1}, "Invalid mutation roster")
        for mutation in panel["mutations"]:
            for index, check in enumerate(mutation["checks"]):
                all_queries.append(check["query"])
                require(check["result"] == ("sat" if index == mutation["target"] else "unsat"), "Mutation outcome changed")
                if check["witness"] is None:
                    continue
                inputs = check["witness"]
                require(legal(task, inputs), "Illegal mutation witness")
                baseline = direct(task, inputs, [2, 3] if task == "sort" else [0, 0])
                target = mutation["target"]
                if task == "withdrawal":
                    output = [False, inputs["balance"]] if target == 0 else [baseline[0], inputs["balance"] + 1]
                elif task == "transfer":
                    output = [inputs["balance"], baseline[1]] if target == 0 else [baseline[0], inputs["recipient"] - 1]
                elif task == "login":
                    output = [False, False, -1] if target == 0 else [baseline[0], not baseline[1], baseline[2]]
                else:
                    output = baseline[::-1] if target == 0 else [baseline[0] - 1, baseline[1]]
                values = properties(task, inputs, output)
                require(not values[target] and values[1 - target], "Non-isolated concrete mutation")
            isolated_mutants += 1
        baseline_id = [2, 3] if task == "sort" else [0, 0]
        for pair in panel["pairs"]:
            all_queries.append(pair["check"]["query"])
            if pair["left"] == baseline_id and not any(example["task"] == task for example in examples):
                examples.append({"task": task, "intended_id": baseline_id, "alternative_id": pair["right"],
                                 "input": pair["check"]["witness"], "intended": pair["left_output"], "alternative": pair["right_output"]})
    require(len(all_queries) == len(set(all_queries)) == report["solver_queries"] == 195, "Query accounting failed")
    require(set(all_queries) == set(report["query_sha256"]), "Unexpected/missing query")
    for name in all_queries:
        require(sha(PILOT / "queries" / name) == report["query_sha256"][name], "Query hash failed")
    payload = json.loads((CONTROLS / "controls.json").read_text(encoding="utf-8"))
    for name, checksum in payload["source_sha256"].items():
        require(sha(ROOT / name) == checksum, "Supplemental source changed")
    total, witnessed = validate_controls(payload, CONTROLS)
    result = {"status": "PASS", "pilot_result_sha256": sha(PILOT / "results.json"),
              "pilot_audit_sha256": sha(PILOT / "audit.json"), "controls_sha256": sha(CONTROLS / "controls.json"),
              "validator_sha256": sha(Path(__file__)), "pilot_queries_accounted": len(all_queries),
              "control_queries_replayed": total, "control_sat_witnesses_checked": witnessed,
              "isolated_mutants_concretely_replayed": isolated_mutants,
              "preserved_failed_control_queries": {path.name: sha(path) for path in sorted((ROOT / "evidence/controls-20261124").glob("*.smt2"))},
              "control_query_sha256": {path.name: sha(path) for path in sorted(CONTROLS.glob("*.smt2"))},
              "summary": audit["summary"], "examples": examples}
    with (ROOT / "evidence/validation-20261124.json").open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    if arguments.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(EvidenceTamperTests)
        outcome = unittest.TextTestRunner(verbosity=2).run(suite)
        raise SystemExit(0 if outcome.wasSuccessful() else 1)
    validate()