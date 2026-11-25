import argparse
import hashlib
import itertools
import json
import platform
import time
from pathlib import Path

import z3


TASKS = ("withdrawal", "transfer", "login", "sort")
ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def variables(task):
    names = {
        "withdrawal": ("balance", "amount"),
        "transfer": ("balance", "amount", "recipient"),
        "login": ("exists", "password", "locked", "admin", "account"),
        "sort": ("left", "right"),
    }[task]
    return {name: z3.Bool(name) if name in ("exists", "password", "locked", "admin")
            else z3.Int(name) for name in names}


def semantics(task, inputs, first, second):
    if task == "withdrawal":
        balance, amount = inputs["balance"], inputs["amount"]
        eligible = z3.And(amount > 0, amount <= balance)
        allowed = (eligible, z3.And(amount > 0, amount < balance),
                   z3.BoolVal(False), z3.BoolVal(True))[first]
        debit = (balance - amount, balance, z3.IntVal(0), balance - 2 * amount)[second]
        return (allowed, z3.If(allowed, debit, balance))
    if task == "transfer":
        balance, amount, recipient = (inputs[name] for name in ("balance", "amount", "recipient"))
        return ((balance - amount, balance, balance - amount - 1, z3.IntVal(0))[first],
                (recipient + amount, recipient, recipient + 2 * amount, recipient + amount + 1)[second])
    if task == "login":
        eligible = z3.And(inputs["exists"], inputs["password"], z3.Not(inputs["locked"]))
        allowed = (eligible, z3.And(inputs["exists"], inputs["password"]),
                   z3.BoolVal(False), z3.BoolVal(True))[first]
        identity = (inputs["account"], z3.IntVal(0), inputs["account"] + 1,
                    z3.If(inputs["admin"], inputs["account"], 0))[second]
        return (allowed, z3.And(allowed, inputs["admin"]), z3.If(allowed, identity, -1))
    left, right = inputs["left"], inputs["right"]
    options = (left, right, z3.If(left <= right, left, right), z3.If(left <= right, right, left))
    return options[first], options[second]


def domain(task, inputs):
    if task == "withdrawal":
        return inputs["balance"] >= 0
    if task == "transfer":
        return z3.And(inputs["balance"] >= inputs["amount"], inputs["amount"] > 0,
                      inputs["recipient"] >= 0)
    if task == "login":
        return inputs["account"] > 0
    return z3.BoolVal(True)


def clauses(task, inputs, output):
    if task == "withdrawal":
        return (output[0] == z3.And(inputs["amount"] > 0, inputs["amount"] <= inputs["balance"]),
                z3.And(output[1] >= 0, output[1] <= inputs["balance"]))
    if task == "transfer":
        return output[0] == inputs["balance"] - inputs["amount"], output[1] >= inputs["recipient"]
    if task == "login":
        return (output[0] == z3.And(inputs["exists"], inputs["password"], z3.Not(inputs["locked"])),
                output[1] == z3.And(output[0], inputs["admin"]))
    return (output[0] <= output[1],
            z3.And(*[z3.And(value >= z3.If(inputs["left"] <= inputs["right"], inputs["left"], inputs["right"]),
                           value <= z3.If(inputs["left"] <= inputs["right"], inputs["right"], inputs["left"]))
                     for value in output]))


def added_intent(task, inputs, output):
    if task == "withdrawal":
        return output[1] == z3.If(output[0], inputs["balance"] - inputs["amount"], inputs["balance"])
    if task == "transfer":
        return output[1] == inputs["recipient"] + inputs["amount"]
    if task == "login":
        return z3.Implies(output[0], output[2] == inputs["account"])
    return z3.Or(z3.And(output[0] == inputs["left"], output[1] == inputs["right"]),
                 z3.And(output[0] == inputs["right"], output[1] == inputs["left"]))


def intended(task):
    return (2, 3) if task == "sort" else (0, 0)


def mutant(task, inputs, clause):
    baseline = semantics(task, inputs, *intended(task))
    if task == "withdrawal":
        return (z3.BoolVal(False), inputs["balance"]) if clause == 0 else (baseline[0], inputs["balance"] + 1)
    if task == "transfer":
        return (inputs["balance"], baseline[1]) if clause == 0 else (baseline[0], inputs["recipient"] - 1)
    if task == "login":
        return (z3.BoolVal(False), z3.BoolVal(False), z3.IntVal(-1)) if clause == 0 else (baseline[0], z3.Not(baseline[1]), baseline[2])
    return (baseline[1], baseline[0]) if clause == 0 else (baseline[0] - 1, baseline[1])


def literal(value):
    return z3.is_true(value) if z3.is_bool(value) else value.as_long()


class EvidenceSolver:
    def __init__(self, directory):
        self.directory = directory
        self.count = 0

    def check(self, predicate, inputs):
        self.count += 1
        solver = z3.Solver()
        solver.set(timeout=5000)
        solver.add(predicate)
        name = f"query-{self.count:05d}.smt2"
        (self.directory / name).write_text(solver.to_smt2(), encoding="utf-8")
        result = solver.check()
        if result == z3.unknown:
            raise RuntimeError(f"Inconclusive {name}: {solver.reason_unknown()}")
        witness = None
        if result == z3.sat:
            model = solver.model()
            witness = {key: literal(model.eval(value, model_completion=True)) for key, value in inputs.items()}
        return {"result": str(result), "query": name, "witness": witness}


def evaluate(output, inputs, witness):
    substitutions = [(inputs[key], z3.BoolVal(value) if isinstance(value, bool) else z3.IntVal(value))
                     for key, value in witness.items()]
    return [literal(z3.simplify(z3.substitute(value, *substitutions))) for value in output]


def run(destination):
    destination.mkdir(parents=True, exist_ok=False)
    queries = destination / "queries"
    queries.mkdir()
    solver = EvidenceSolver(queries)
    start = time.perf_counter()
    sources = {name: digest(ROOT / name) for name in ("PLAN.md", "requirements.txt", "counterworlds.py", "audit.py", "test_counterworlds.py")}
    report = {"kind": "constructed-symbolic-pilot", "python": platform.python_version(),
              "z3": z3.get_version_string(), "source_sha256": sources, "tasks": []}
    for task in TASKS:
        inputs = variables(task)
        precondition = domain(task, inputs)
        candidates = []
        for first, second in itertools.product(range(4), repeat=2):
            output = semantics(task, inputs, first, second)
            contract = z3.And(*clauses(task, inputs, output))
            weak = solver.check(z3.And(precondition, z3.Not(contract)), inputs)
            strong = solver.check(z3.And(precondition, z3.Not(z3.And(contract, added_intent(task, inputs, output)))), inputs)
            candidates.append({"id": [first, second], "weak": weak, "strong": strong})
        mutations = []
        for target in range(2):
            properties = clauses(task, inputs, mutant(task, inputs, target))
            checks = [solver.check(z3.And(precondition, z3.Not(prop)), inputs) for prop in properties]
            mutations.append({"target": target, "checks": checks})
        pairs = []
        for left, right in itertools.combinations(candidates, 2):
            if left["weak"]["result"] != "unsat" or right["weak"]["result"] != "unsat":
                continue
            left_output = semantics(task, inputs, *left["id"])
            right_output = semantics(task, inputs, *right["id"])
            check = solver.check(z3.And(precondition, z3.Or(*[before != after for before, after in zip(left_output, right_output)])), inputs)
            pair = {"left": left["id"], "right": right["id"], "check": check,
                    "both_strong": left["strong"]["result"] == right["strong"]["result"] == "unsat"}
            if check["witness"] is not None:
                pair["left_output"] = evaluate(left_output, inputs, check["witness"])
                pair["right_output"] = evaluate(right_output, inputs, check["witness"])
            pairs.append(pair)
        report["tasks"].append({"task": task, "candidates": candidates, "mutations": mutations, "pairs": pairs})
    report["solver_queries"] = solver.count
    report["elapsed_seconds"] = time.perf_counter() - start
    report["query_sha256"] = {path.name: digest(path) for path in sorted(queries.glob("*.smt2"))}
    if any(digest(ROOT / name) != checksum for name, checksum in sources.items()):
        raise RuntimeError("Sources changed during execution")
    (destination / "results.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(destination), "queries": solver.count, "elapsed_seconds": report["elapsed_seconds"]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    run(parser.parse_args().out)