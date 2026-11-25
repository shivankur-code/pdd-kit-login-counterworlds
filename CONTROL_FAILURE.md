# Preserved control failure and interpretation

The first supplemental run, `evidence/controls-20261124`, failed at the login
full-output uniqueness check. Its nine SMT queries remain untouched. No original
pilot input or result was changed, and that directory must not be reused.

The stronger login contract constrains identity only on success. Its output
relation permits different identity values on rejection. All original grammar
candidates normalize that unused field to -1, so a unique surviving candidate
was not evidence of full relational uniqueness. This falsifies the proposed
full-tuple uniqueness expectation for login. It does not refute its accepted
implementation or its success-identity guarantee.

The corrected supplement records BOTH the full-tuple check (SAT expected for
login, UNSAT for the other three) and an explicitly declared observable-output
projection: login refusal observes (allowed, admin_flag, -1), not the unused
identity field. Successful login observes the full tuple. No projection applies
to the other tasks. This is a declared semantic choice, not a bug label and not
an inference about what a real application's clients observe. If an API exposes
the raw rejected identity, that difference remains observable there.

Repeat only the supplemental controls in a new directory,
`evidence/controls-v2-20261124`, recording sixteen queries. Preserve this failure
in the final report. The initial result was obtained before adding this projection;
the corrected supplement is exploratory/post-pilot, not preregistered confirmation.