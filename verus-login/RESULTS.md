# The login that keeps every promise and still logs everyone out

Ran locally on 2026-11-24 on a Windows ARM64 laptop. Paid compute: $0. No GPU
and no AI model calls.

## Start with a concrete example

Ana opens the Pet Store and logs in with the right email and password. The
server answers with a **token**: a signed note that says "this is customer
Ana, valid until a certain time". Her browser shows that note with every later
request, and the server accepts it until the time written on it runs out.

The login code reads the clock once and gets two numbers: `now`, the current
time, and `exp` (expiry), which is `now` plus 24 hours. Suppose an AI agent writing
the code makes a one-word slip and writes `now` where it should write `exp`.
Ana's token now says "valid until right now". With the usual token-checking
settings, the server keeps accepting it for about one more minute, then logs
her out. The same happens to every customer, every time.

We gave that slip to **Verus**, the proof tool PDD Kit uses, together with PDD
Kit's own published login contract, unchanged. Verus accepted it: every one of
the eight promises the contract makes about login is still proved.

## The words used below

- **PDD Kit**: a November 2026 prototype from GitHub Next and Microsoft
  Research. Instead of reviewing the code an AI agent writes, people review a
  **contract**: a list of promises the code must keep.
- **`ensures` clause**: one promise, such as "if a token comes back, the
  password was right". It describes what is true when a function returns.
- **Verus**: a tool that checks Rust code against its contract for every
  possible input, not just test examples. "Verified" means it found a proof;
  "rejected" means it could not, and it names the promise that failed.
- **Trusted wrapper**: a small function Verus cannot look inside, such as the
  database, password hashing, the clock, or token signing. A person accepts
  its promise and tests check it.
- **Mutant**: a deliberately planted bug. PDD Kit plants one per promise and
  confirms Verus rejects each one. That shows each promise catches something.
- **Counterworld** (our term): a different implementation that keeps every
  promise but behaves differently in a way someone would care about.
  A mutant asks "does each promise catch something?" A counterworld asks
  "what does the contract still let through?"

## What we did

1. **Got the real contract.** The PDD Kit page shows its login file,
   `verified/src/login.rs`, inside an interactive figure. We extracted all 368
   lines from the page's script, then re-downloaded and re-extracted them to
   confirm the same SHA-256 fingerprint (hash) `b8dc10d0…1c57`.
2. **Built a model Verus can check.** The Pet Store backend code is not
   public, so types such as the database connection are minimal stand-ins.
   All contract text is copied. The page leaves the five proved functions
   empty (`unimplemented!()`), so we wrote bodies that follow the page's
   flowchart. See [login_model.template.rs](login_model.template.rs). It
   holds only the stand-ins and bodies written for this study. Each
   `//@published A-B` line stands for lines A to B of PDD Kit's file, which
   [build_model.py](build_model.py) fills in to recreate the exact model that
   was checked.
3. **Checked the copy mechanically.** Every published contract line must
   appear in the model, in order. 268 lines are identical, 6 are identical
   after replacing the `sqlx::` type path, and 6 are regrouped (explained
   below). No line was added between them, and the list of trusted functions
   is exactly the published one. To show this check is not toothless, five
   tampered copies were tried: a weakened promise, an added precondition, a
   proved function marked trusted, an extra declaration, and an unproved
   lemma. The check rejected all five.
4. **Ran Verus 0.2026.11.22** (native ARM64 build, published download hash
   checked) on 14 versions of the file. Each version differs from the
   reference by a few listed text edits. See [study.py](study.py).

## Results

| Version | What changes | Verus result |
| --- | --- | --- |
| Reference | Signs the token with the clock's 24-hour expiry | Verified: 8 functions, 0 errors |
| Published clauses as written | The 6 regrouped clauses put back exactly as published | Stops before proving: 6 front-end errors (errors found before the proof starts) |
| 5 PDD Kit mutants | One published bug each | All 5 rejected |
| **Expired on arrival** | Writes `expiry.now` instead of `expiry.exp` | **Verified** |
| **Never expires** | Writes the largest possible number as the expiry | **Verified** |
| Secret in error | A database failure returns the token-signing secret as the error text | Verified |
| Reference + proposed repair | Two new expiry promises added | Verified |
| Expired on arrival + repair | | Rejected, at the new expiry promise |
| Never expires + repair | | Rejected, at the new expiry promise |
| Secret in error + repair | | Verified (the repair only covers expiry) |

Every version met its expected outcome. Those expectations were written into
the harness before its first run. The one exception is the "published clauses
as written" check, which was added afterwards to record the six errors already
seen. Each Verus run took between 0.4 and 3.2 seconds.

### Our model rejects PDD Kit's own mutants

This is the check that our model is faithful where PDD Kit tested it. Verus
checks each function separately, so it reports the failing promise of the
function where the bug sits. PDD Kit's labels name the matching promise of the
whole login.

| PDD Kit mutant | Promise Verus said failed | PDD Kit says it breaks |
| --- | --- | --- |
| Refuse everyone | "The right password for a found row always gets claims." | c3: the right password always gets a token |
| Skip the password check | "Claims come back only for a found row whose stored hash matches the password." and the wrong-password promise | c2 and c5 |
| Check the username first | "An email, when sent, wins: customers are searched for exactly that email." | c2, c7, c8 |
| Report a database outage as 401 | "Failed lookup: 500." | c3 |
| Treat an unreadable hash as a wrong password | "A found row whose hash bcrypt cannot read gets no claims." | c6 |

Some mutants also failed an extra promise, such as the unreadable-hash
promise for "refuse everyone". That is expected, because the planted bug
changes more than one behavior.

## Why the expiry gap exists

- **No promise mentions expiry.** The token's claims (`sub` = account id,
  `role`, `exp` = expiry) are signed together, but the promises pin only `sub`
  and `role`. The function that signs the token has the doc comment "signs a
  token from Ok claims with a 24-hour expiry", and the page's explorer says
  "expiring 24 hours after the clock reading". Neither is an `ensures` clause.
- **The clock wrapper is correct, and that is not enough.** The planned test
  `expiry_is_24_hours_after_the_clock_reading` checks that the clock wrapper
  computes `exp = now + 24 hours`. The slip is not in the wrapper. It is in the
  proved code that decides which of the two numbers to sign.
- **The mutation check cannot see it.** PDD Kit plants one mutant per promise.
  No promise is about expiry, so no mutant targets it. This is not a fault in
  mutation checking; it measures whether written promises catch bugs, not
  which promises are missing.
- **It touches the first decision PDD Kit highlights.** The page's first
  decision card asks for both directions ("Both ways"): the right password
  must always get a token, which rules out "a login that refuses everyone".
  The clock's trust card says, if the clock were wrong, "Tokens would expire
  at another time. Neither of the two requirements depends on it." In the
  "expired on arrival" counterworld, the right password still gets a token on
  paper. If the server checks expiry in the usual way, though, that token stops
  working within about a minute. For users, that is close to the
  refuse-everyone login the decision card was meant to exclude.

"The usual way" is an assumption. The common Rust library `jsonwebtoken`
checks expiry by default and allows 60 seconds of clock difference
([its `Validation` documentation](https://docs.rs/jsonwebtoken/latest/jsonwebtoken/struct.Validation.html)).
The Pet Store's token-checking code is not published, so we do not know its
settings.

## A proposed repair (a question for the authors, not a fix)

We added two promises in the same style the page already uses for the
database, where `customer_on_file` means the row on file "when login looks":

- `clock_at_login()`: the clock reading when login looks, left abstract.
  The clock wrapper promises its `now` is that reading.
- The token-signing function and the whole login promise: the token's
  expiry is exactly `clock_at_login() + 86,400` seconds.

With these, the reference still verifies and both expiry counterworlds are
rejected, each at the new promise. The secret-in-error counterworld still
verifies, which shows the repair is narrow.

The repair has a cost. The clock becomes part of the trusted contract, and two
clock readings in one login are treated as one reading. That is the same
simplification the page already makes for the database. The authors may
instead prefer to keep token lifetime outside the proof. Then a cheaper
change is to list it under "Not promised" and add a test that login uses the
clock wrapper's expiry. Either way, it becomes a recorded decision instead of
an unwritten one.

## A second, smaller question: the text of a database error

When the database lookup fails, the contract promises only "some 500
(internal server error)". The page's explorer and the `database_error` comment
say the 500 carries sqlx's message "as today". By contrast, the 500 for an
unreadable password hash is pinned exactly to bcrypt's message. Verus accepts
a version that puts the token-signing secret into the database 500. Whether
this matters depends on whether 500 texts reach users or logs, and the code
that turns errors into responses is not published. This is a question, not a
reported vulnerability.

## Also found: six published clauses need regrouping for current Verus

Verus 0.2026.11.22 stops on six of the published clauses before proving
anything. Its rules limit where a name created by `matches` can be used. We
regrouped those clauses without changing their meaning. We either added
parentheses or wrote "(A and B) implies C" as the equivalent
"A implies (B implies C)". Running the clauses exactly as published reproduces
the six errors, and that run is part of the evidence. The page says PDD Kit's
first build step fixes front-end errors without changing promises, so this is
probably expected and may reflect a different Verus version. The six
rewrites are listed in [study.py](study.py) (`REGROUPINGS`).

## What went wrong along the way (kept, not hidden)

1. The first Verus run of the model stopped on the six clauses above. That led
   to the regrouping and to the "published clauses as written" check.
2. The harness first refused to run because the cached published file had
   Windows line endings. The hash is now computed on the text with Unix line
   endings, as originally extracted.
3. The harness crashed on a host stand-in whose `{` sat at the end of a line;
   the contract reader was fixed.
4. **First final run, [`verus-login-20261124`](../evidence/verus-login-20261124/):
   all 14 versions failed before Verus started.** The output folder was given
   as a relative path, but Verus ran from inside that folder. This was a
   harness bug, not a Verus result. The run is kept as recorded.
5. Second final run, `verus-login-v2-20261124`: all checks passed, but saved
   command lines contained a local folder path with a username. It is kept
   privately and not published. The harness now stores only file names.
6. **Shareable run, [`verus-login-v3-20261124`](../evidence/verus-login-v3-20261124/results.json):
   all checks passed.** Results hash
   `e4fecb56fab87d5ea603ff5939e1ab35f6b843c6a383b4ca02866271a0faa1c9`.

The 14 checked `.rs` files are not published, because they contain PDD Kit's
contract text. `results.json` records each file's SHA-256, and rerunning the
study recreates them. Verus's output for each one is included.

Before the final runs, four development runs went to a scratch folder outside
the repository. They used the same model and differed only in harness fixes.

## What this supports

For PDD Kit's published login contract, as extracted on 2026-11-24 and checked
with stand-in host types, Verus accepts implementations that issue tokens that
are already expiring or never expire. The same model rejects all five of PDD
Kit's published mutants, so it is not looser than PDD Kit where PDD Kit tested
it. A two-promise addition closes this specific gap in the model.

## What this does not support

- **Not a bug in the Pet Store.** We never saw its code; it very likely signs
  the right expiry. The point is that the proof would not notice if it did
  not.
- **Not a demonstrated exploit.** The token checker's settings are unknown.
- **Not a claim that PDD Kit's tests miss it.** Only the test names are
  published. An end-to-end test that reads the token within a minute would
  pass "expired on arrival"; one that checks `exp` would catch it.
- **Not a criticism of the method.** The page's "Not promised" ring includes
  "what nobody wrote down". This is a concrete example of an item in that
  ring that the explorer and a doc comment do describe.
- **Not a novelty claim.** Whether specifications are complete enough has
  been studied for a long time. The contribution is a concrete, checkable
  question about one published specification.
- **Model limits.** Host types are stand-ins, trusted bodies are stubs,
  nothing was executed, and async behavior is as Verus models it.

## Reproduce

Requires Python 3 and Verus 0.2026.11.22 with its Rust toolchain. `study.py`
looks for `verus-arm64-win/verus.exe`, `rustup/` and `cargo/` under
`--verus-home`, which defaults to `%LOCALAPPDATA%\pdd-verus`. This is the layout
used for the run on Windows ARM64. On another platform, put or link the Verus
release at that path. The published file defaults to
`%LOCALAPPDATA%\pdd-counterworlds-source\published-login.rs`, and `--published`
overrides it.

```powershell
python fetch_published.py                       # download PDD Kit's file; refuses if the page changed
python build_model.py                           # recreate login_model.rs; refuses if it differs from the studied model
python study.py --out ..\evidence\my-verus-run  # refuses to overwrite an existing folder
```
