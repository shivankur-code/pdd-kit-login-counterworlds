# Counterworlds pilot, 2026-11-24

## Question fixed before execution

Can every stated clause reject its designated, clause-isolated mutation while
the same contract admits behaviorally different implementations? Does an explicit
missing-intent clause remove the differences in the declared candidate grammar?

This is a constructed demonstration, not a random benchmark, human study, novelty
claim, evaluation of PDD Kit, or test of its unpublished implementation. The
author of this pilot deliberately chooses incomplete contracts. Counts must not
be represented as real-world failure rates or independent statistical samples.

## Fixed scope

Four tasks, each with sixteen implementations from a 4-by-4 grammar:

| Task | Existing clauses | Additional intent |
| --- | --- | --- |
| Withdrawal | Exact accept/reject decision; balance stays in range | Exact debit and no balance change on refusal |
| Transfer | Exact sender debit; recipient never loses money | Recipient receives exactly the amount |
| Login | Exact accept/reject decision; exact admin flag | Successful response identifies the authenticated account |
| Sort two integers | Ordered result; each result within input bounds | Preserve the input multiset |

For each task, two designated mutants each violate their targeted clause and
satisfy the other clause. These are selected demonstration mutations, not an
implementation of PDD Kit's mutation generator. Candidate enumeration does not
adapt to observed outcomes. Compare all accepted candidate pairs. Include both
equivalent and disagreeing candidates; equivalence is observational, not textual.

Use Z3 on mathematical integers and booleans. A solver UNSAT response to the
existential negation establishes the encoded universal property, conditional on
the encoding and solver. SAT supplies a counterexample. UNKNOWN and timeout are
errors, never proof or equivalence. Archive SMT-LIB queries and results. Witnesses
are reproducible but not claimed globally smallest. Bound each solver call at
five seconds; no model inference, remote GPU, credentials, or paid resources.

## Validation and controls

Run unittest before the experiment. After execution, independently evaluate all
candidates and replay witnesses using direct Python formulas on an exhaustive
small domain. This is finite cross-checking, not a second universal proof. Verify
source digests and evidence digests, require an exclusive new output directory,
and save all candidate and pair outcomes, not only favorable examples. Strong
contracts and observationally equivalent pairs are negative controls. Check that
the original intended implementation survives each contract.

The audit must check every accepted candidate, every recorded disagreement, both
designated mutations per task, and strong-contract survivors. No human preference
will be inferred from these constructed examples. A later study needs independent
tasks, real code integration, competing methods and human review measurements.

## Artifacts

Run with `python counterworlds.py --out evidence/pilot-20261124`.
Audit with `python audit.py evidence/pilot-20261124`.
The result includes full candidate identities, contract outcomes, disagreements,
solver queries, Python and Z3 versions, source SHA-256 values, and elapsed time.
Reports must distinguish symbolic results from finite replay and disclose limits.