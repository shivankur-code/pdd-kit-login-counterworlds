# PDD Counterworlds: a constructed symbolic pilot

This is an independent study, not part of PDD Kit. PDD Kit's contract text is
not included here; [verus-login/fetch_published.py](verus-login/fetch_published.py)
downloads it from the [PDD Kit page](https://githubnext.com/projects/pdd-kit/).

**Newest result:** [verus-login/RESULTS.md](verus-login/RESULTS.md) checks PDD
Kit's published login contract with real Verus. It finds implementations that
keep every published promise but issue tokens that are already expiring or
never expire. Reproduction steps are at the end of that report. The shareable
evidence is
[evidence/verus-login-v3-20261124/results.json](evidence/verus-login-v3-20261124/results.json).
The failed first run, `evidence/verus-login-20261124/`, is kept. The second
run is not published, because its saved commands include a local folder path.

The rest of this page covers the earlier Z3 pilot.
Start with [RESULTS.md](RESULTS.md) for what actually ran and what it does not
establish.
[PLAN.md](PLAN.md) was written before the pilot. Later controls and the failure
are recorded separately in [CONTROL_AMENDMENT.md](CONTROL_AMENDMENT.md) and
[CONTROL_FAILURE.md](CONTROL_FAILURE.md).

## Reproduce in a fresh directory

Requires Python and the pinned dependency in [requirements.txt](requirements.txt).
Create an isolated environment, install the requirement, and run from this folder:

```powershell
python -m pip install -r requirements.txt
python -m unittest -v test_counterworlds
python counterworlds.py --out evidence/my-fresh-pilot
python audit.py evidence/my-fresh-pilot
python controls.py --out evidence/my-fresh-controls
```

Output directories are exclusive: existing evidence is not overwritten. The
included original pilot and corrected supplement are already completed. Do not
rerun into their output directories. Equivalent formulas may receive different
valid solver witnesses across solver/platform versions.

## Check the included saved evidence

The original audit was executed and saved. The additional validator checks the
included source hashes, result/audit binding, candidate and pair rosters, mutation
witnesses, query hashes, and supplemental controls. Its final validation receipt
already exists, so the default validator intentionally refuses to overwrite it.
Its test mode is repeatable and does not change saved evidence:

```powershell
python validate_evidence.py --self-test
```

The validator is specific to the included artifact layout; it is not a generic
auditor for arbitrary third-party proofs. Both auditors were authored alongside
the prototype. Separate Python formulas and solver-query replay reduce some
implementation risks, but are not independent third-party verification.

## Main artifacts

- [evidence/pilot-20261124/results.json](evidence/pilot-20261124/results.json): all 64 candidates, 51 pair checks, 8 mutations, source/query digests.
- [evidence/pilot-20261124/audit.json](evidence/pilot-20261124/audit.json): original successful finite and solver replay audit.
- [evidence/controls-v2-20261124/controls.json](evidence/controls-v2-20261124/controls.json): equivalent rewrites and relational uniqueness checks.
- [evidence/validation-20261124.json](evidence/validation-20261124.json): final saved-evidence validation and four concrete examples.
- `evidence/controls-20261124/`: nine queries from the failed first control run, retained rather than overwritten.

No remote GPU, credentials, LLM generation, or paid resources are required.
These are mathematical models and finite implementation grammars, not proofs
about deployed services, measured human outcomes, or established novel research.

## Context

- [Official PDD Kit project](https://githubnext.com/projects/pdd-kit/).
- [CounterExample Guided Neural Synthesis](https://arxiv.org/abs/2001.09245): one relevant established ingredient; not an exhaustive related-work review.