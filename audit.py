import argparse
import hashlib
import itertools
import json
from pathlib import Path

import z3


def direct(task, inputs, candidate):
    first, second = candidate
    if task == "withdrawal":
        balance, amount = inputs["balance"], inputs["amount"]
        allowed = (0 < amount <= balance, 0 < amount < balance, False, True)[first]
        after = (balance - amount, balance, 0, balance - 2 * amount)[second] if allowed else balance
        return [allowed, after]
    if task == "transfer":
        balance, amount, recipient = inputs["balance"], inputs["amount"], inputs["recipient"]
        return [(balance - amount, balance, balance - amount - 1, 0)[first],
                (recipient + amount, recipient, recipient + 2 * amount, recipient + amount + 1)[second]]
    if task == "login":
        allowed = (inputs["exists"] and inputs["password"] and not inputs["locked"],
                   inputs["exists"] and inputs["password"], False, True)[first]
        identity = (inputs["account"], 0, inputs["account"] + 1,
                    inputs["account"] if inputs["admin"] else 0)[second]
        return [allowed, allowed and inputs["admin"], identity if allowed else -1]
    left, right = inputs["left"], inputs["right"]
    values = (left, right, min(left, right), max(left, right))
    return [values[first], values[second]]


def properties(task, inputs, output):
    if task == "withdrawal":
        eligible = 0 < inputs["amount"] <= inputs["balance"]
        return [output[0] == eligible, 0 <= output[1] <= inputs["balance"],
                output[1] == (inputs["balance"] - inputs["amount"] if output[0] else inputs["balance"])]
    if task == "transfer":
        return [output[0] == inputs["balance"] - inputs["amount"], output[1] >= inputs["recipient"],
                output[1] == inputs["recipient"] + inputs["amount"]]
    if task == "login":
        return [output[0] == (inputs["exists"] and inputs["password"] and not inputs["locked"]),
                output[1] == (output[0] and inputs["admin"]), not output[0] or output[2] == inputs["account"]]
    return [output[0] <= output[1], all(min(inputs.values()) <= value <= max(inputs.values()) for value in output),
            sorted(output) == sorted(inputs.values())]


def finite_inputs(task):
    if task == "login":
        for values in itertools.product((False, True), repeat=4):
            for account in range(1, 5):
                yield dict(zip(("exists", "password", "locked", "admin", "account"), (*values, account)))
    elif task == "sort":
        for left, right in itertools.product(range(-3, 5), repeat=2):
            yield {"left": left, "right": right}
    elif task == "withdrawal":
        for balance, amount in itertools.product(range(7), range(-2, 9)):
            yield {"balance": balance, "amount": amount}
    else:
        for balance, amount, recipient in itertools.product(range(7), range(1, 7), range(7)):
            if amount <= balance:
                yield {"balance": balance, "amount": amount, "recipient": recipient}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def audit(directory):
    report = json.loads((directory / "results.json").read_text(encoding="utf-8"))
    root = Path(__file__).resolve().parent
    for name, checksum in report["source_sha256"].items():
        require(sha(root / name) == checksum, f"Source changed: {name}")
    require(len(report["tasks"]) == 4, "Missing tasks")
    checks = []
    summary = []
    finite_evaluations = 0
    for panel in report["tasks"]:
        task = panel["task"]
        require(len(panel["candidates"]) == 16, "Missing candidates")
        for candidate in panel["candidates"]:
            checks.extend([candidate["weak"], candidate["strong"]])
            for inputs in finite_inputs(task):
                props = properties(task, inputs, direct(task, inputs, candidate["id"]))
                finite_evaluations += 1
                if candidate["weak"]["result"] == "unsat":
                    require(all(props[:2]), "Finite replay contradicts weak proof")
                if candidate["strong"]["result"] == "unsat":
                    require(all(props), "Finite replay contradicts strong proof")
            for strength in ("weak", "strong"):
                witness = candidate[strength]["witness"]
                if witness is not None:
                    props = properties(task, witness, direct(task, witness, candidate["id"]))
                    require(not all(props[:2] if strength == "weak" else props), "Invalid rejection witness")
        for mutation in panel["mutations"]:
            checks.extend(mutation["checks"])
            for index, check in enumerate(mutation["checks"]):
                require(check["result"] == ("sat" if index == mutation["target"] else "unsat"), "Non-isolated mutation")
        weak = [candidate for candidate in panel["candidates"] if candidate["weak"]["result"] == "unsat"]
        strong = [candidate for candidate in panel["candidates"] if candidate["strong"]["result"] == "unsat"]
        require(len(panel["pairs"]) == len(weak) * (len(weak) - 1) // 2, "Missing pair checks")
        for pair in panel["pairs"]:
            checks.append(pair["check"])
            witness = pair["check"]["witness"]
            if witness is not None:
                before, after = direct(task, witness, pair["left"]), direct(task, witness, pair["right"])
                require(before == pair["left_output"] and after == pair["right_output"] and before != after, "Invalid disagreement replay")
                require(all(properties(task, witness, before)[:2]) and all(properties(task, witness, after)[:2]), "Witness violates base contract")
            else:
                require(all(direct(task, inputs, pair["left"]) == direct(task, inputs, pair["right"])
                            for inputs in finite_inputs(task)), "False equivalence")
            require(not pair["both_strong"] or pair["check"]["result"] == "unsat", "Strong contract still ambiguous")
        summary.append({"task": task, "candidates": 16, "weak_accepted": len(weak), "strong_accepted": len(strong),
                        "weak_disagreeing_pairs": sum(pair["check"]["result"] == "sat" for pair in panel["pairs"]),
                        "weak_equivalent_pairs": sum(pair["check"]["result"] == "unsat" for pair in panel["pairs"]),
                        "strong_disagreeing_pairs": sum(pair["both_strong"] and pair["check"]["result"] == "sat" for pair in panel["pairs"])})
    require(len(checks) == report["solver_queries"] == len(report["query_sha256"]), "Query count mismatch")
    for check in checks:
        path = directory / "queries" / check["query"]
        require(sha(path) == report["query_sha256"][path.name], "Query digest mismatch")
        solver = z3.Solver()
        solver.set(timeout=5000)
        solver.from_file(str(path))
        require(str(solver.check()) == check["result"], "Archived solver result not reproducible")
    result = {"status": "PASS", "results_sha256": sha(directory / "results.json"),
              "symbolic_queries_rechecked": len(checks), "finite_candidate_evaluations": finite_evaluations,
              "summary": summary, "limits": "Constructed examples; same solver replay; independent finite Python encoding, not independent universal proof."}
    with (directory / "audit.json").open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    audit(parser.parse_args().directory)