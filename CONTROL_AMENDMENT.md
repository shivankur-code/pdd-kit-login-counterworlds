# Supplemental controls, 2026-11-24

The fixed pilot completed before this file was written. Its 64-candidate grammar
contained no accepted observationally equivalent pairs; each strengthened
contract accepted just one candidate. Reporting zero disagreeing strong pairs
alone is therefore a weak control. Preserve the original protocol, code and
evidence unchanged. This supplement is post-pilot, not preregistered.

Add four explicitly equivalent, syntactically different rewrites and ask the
solver whether any legal input distinguishes each from the intended function.
Expected: UNSAT. This is a check against treating every textual difference as an
intent gap. It is not a measured false-positive rate on natural code.

Separately, quantify symbolically over two arbitrary output tuples at a shared
input, without restricting them to the candidate grammar. Ask whether both can
obey the weak contract and disagree (expected SAT), and whether both can obey
the strong contract and disagree (expected UNSAT). This checks output uniqueness
of these mathematical relations, not program liveness, hidden side effects,
concurrency, compiler correctness or real-world specification completeness.

Run `python controls.py --out evidence/controls-20261124`. Archive all twelve
queries, witnesses, and source digests. The original independent finite audit
does not cover this supplement; validate it separately by replaying queries and
checking concrete SAT witnesses against the separately encoded Python contracts.