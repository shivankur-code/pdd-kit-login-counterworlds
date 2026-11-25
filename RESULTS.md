# Two products, one green contract

Completed locally on 2026-11-24. Paid compute: $0. No GPU rented, no model
inference, no author contact.

> **Follow-up on PDD Kit's own contract:** the same question, asked with real
> Verus about PDD Kit's published Pet Store login, is in
> [verus-login/RESULTS.md](verus-login/RESULTS.md). That study does not change
> anything in this pilot.

## Start with a concrete example

A transfer starts with sender balance 1, recipient balance 0, and amount 1.
The contract says: debit the sender by exactly 1, and never reduce the recipient's
balance. One implementation produces balances (0, 1). Another produces (0, 0):
the money disappears. Both satisfy that contract for every legal mathematical
input. Both selected clause-targeted bugs are rejected by that same contract.

The missing requirement is that the recipient receives exactly the amount.
Adding it excludes the money-disappearing implementation. This example is
deliberately constructed, not a bug found in a real payment system.

## What ran

Enumerated a fixed 4-by-4 implementation grammar for each of four tasks: 64
encoded candidates total. Z3 4.15.4 checked each candidate against an original
contract and a stronger contract, and compared every pair that passed the
original contract. Each task also had two deliberately selected mutations, one
per original clause. Each mutation fails its targeted clause and satisfies the
other clause, so rejection is not merely an unrelated failure.

All queries use mathematical integers and booleans. UNSAT means no violating
input exists in that encoded model; SAT supplies an explicit witness. These are
checks of symbolic program expressions, not proofs of arbitrary Python, Rust,
machine code, termination, or a deployed service. A five-second query timeout
was configured. Unknown results would abort, not count as proofs.

| Constructed task | Candidates | Pass original | Pass stronger | Disagreeing original-contract pairs |
| --- | ---: | ---: | ---: | ---: |
| Withdrawal | 16 | 3 | 1 | 3 |
| Transfer | 16 | 4 | 1 | 6 |
| Login identity | 16 | 4 | 1 | 6 |
| Sort two integers | 16 | 9 | 1 | 36 |
| Total | 64 | 20 | 4 | 51 |

All 8 selected mutations were rejected. Nevertheless, all four original
contracts allowed distinct behaviors. The 51 pairs are highly dependent
combinations of the 20 accepted candidates, not 51 independent findings or
real-world failure rates. The grammar and intentionally incomplete contracts
were chosen by the experiment author; this is not an unbiased benchmark.

## Four machine-generated witnesses

| Task | Shared input | Intended output | Alternative passing output |
| --- | --- | --- | --- |
| Withdrawal | balance 1, amount 1 | allowed, balance 0 | allowed, balance 1 |
| Transfer | sender 1, amount 1, recipient 0 | balances (0, 1) | balances (0, 0) |
| Login | account 1 exists, right password, unlocked, non-admin | allowed, non-admin, account 1 | allowed, non-admin, account 0 |
| Sort | (1, 0) | (0, 1) | (1, 1) |

The withdrawal and login contracts already require exact acceptance decisions;
the findings do not depend on the familiar reject-everyone loophole. Witnesses
are reproducible solver outputs, not claimed globally smallest examples.

## Validation and controls

- 3 pre-experiment unittest methods passed, including per-task subtests.
- 195 original solver queries archived and replayed successfully by the auditor.
- 5,632 candidate/input evaluations cross-checked with separately written Python
  formulas on exhaustive small domains. This is finite evidence, not a second
  independent universal proof or an independently authored audit.
- All 8 selected mutation counterexamples independently replayed concretely.
- All original source and query digests and complete candidate/pair rosters
  checked against saved evidence.
- 4 additional saved-evidence tests passed, including rejecting a missing task,
  a false uniqueness claim, and a fabricated witness.
- 4 explicitly equivalent rewrites correctly produced no distinguishing input.
- 16 final supplemental solver queries replayed; all 5 SAT witnesses checked
  against the separate Python contracts. These are post-pilot controls.

The original pilot took 1.53 seconds of recorded study time on this machine,
excluding installation, tests and audits. This is not a performance benchmark.

## A failed control that improved the interpretation

The first supplemental run failed at login full-output uniqueness. Its nine
queries are preserved. The stronger login contract constrains account identity
only on success, so rejected results may still contain different unused identity
values. Our candidate grammar had silently fixed those values to -1.

Therefore one surviving candidate does NOT establish a complete contract.
The full-output uniqueness check remains SAT for login. Under an explicitly
declared observation rule that ignores identity on rejection, the stronger
contract uniquely determines the observed result. The other three stronger
contracts uniquely determine their full modeled output tuples. Those uniqueness
checks quantify over arbitrary typed outputs, not just grammar candidates.

Ignoring the rejected identity is a semantic choice. If a real API exposes that
field, the difference remains observable. We did not relabel this freedom as a
bug or erase the failed control. See CONTROL_FAILURE.md and CONTROL_AMENDMENT.md.

## What this supports

A demonstration of the distinction between selected-mutation sensitivity and
remaining contractual freedom. A practical prototype can return paired,
contract-satisfying behaviors as executable review questions, while distinguishing
meaningful decisions from intentionally ignored details.

## What this does not support

No new theorem, established research novelty, measured human-review benefit,
production scalability, LLM performance, or failure rate for real specifications.
No evaluation of PDD Kit, Verus or its unpublished mutation generator. PDD Kit's
published login specification already binds the password and token to the same
account; our intentionally weaker login case is NOT a flaw in that example.
No concurrency, external-assumption fault injection, or API-sequence experiments
were run. The two other counterworld categories discussed earlier remain ideas.

Known ingredients include specification adequacy, counterexample-guided
synthesis, equivalence checking, and interactive specification refinement.
The potential contribution is a useful workflow and its measured effect on
review decisions, not discovering that specifications can be incomplete.

## Next discriminating experiment

Before a major novelty pitch: implement the workflow on actual Verus contracts
and production-path functions, include independently selected tasks, compare
against conventional mutation testing and agent-only questions, and measure
review correctness at equal human-time budgets. Include adequate specifications
and deliberately acceptable nondeterminism as controls. Freeze outcomes before
evaluation. GPU generation would be justified only after this design is fixed;
it is not needed to multiply these constructed examples.