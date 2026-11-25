"""Verus counterworld study of the login contract PDD Kit published for its Pet Store example.

What this does, in order:
1. Checks that the published contract text survives unchanged in login_model.rs (fidelity check),
   and that the fidelity check itself notices two planted tampering edits (negative controls).
2. Runs real Verus on the reference model, on PDD Kit's five published mutants, on three
   "counterworld" implementations, and on a proposed contract repair.
3. Writes every input, output, hash and outcome to a new evidence directory, failures included.

Usage:
    python study.py [--out DIR] [--published PATH] [--verus-home DIR]

The evidence directory must not exist yet; the script refuses to overwrite earlier evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODEL = HERE / "login_model.rs"
PAGE_URL = "https://githubnext.com/projects/pdd-kit/"
ASSET_URL = "https://githubnext.com/_astro/SpecTour.CPfG4xDY.js"
ASSET_SHA256 = "35c12fb4b440e391c5600403e5214a72128ac4e0291159fbcb665cc629506b8a"
PUBLISHED_SHA256 = "b8dc10d0e3243fdce7c2f9ee72d8dd06219843633a7221d92f6220991d471c57"
LOCAL = Path(os.environ.get("LOCALAPPDATA", str(Path.home())))
DEFAULT_PUBLISHED = LOCAL / "pdd-counterworlds-source" / "published-login.rs"
DEFAULT_VERUS_HOME = LOCAL / "pdd-verus"

# ---------------------------------------------------------------- fidelity rules

# Host crate paths the stand-ins replace, applied to published lines before comparison.
SUBSTITUTIONS = [("sqlx::SqlitePool", "SqlitePool"), ("sqlx::Error", "SqlxError")]

# Verus rejects these six published clauses before proving anything (front-end scoping of
# `matches` bindings). Each regrouping keeps the meaning: parentheses only, or
# "(A and B) implies C" rewritten as "A implies (B implies C)".
REGROUPINGS = [
    (
        "        r matches Ok(t) ==> (named_account(email, username) matches Some(a) && password_matches(password@, a.password_hash) && token_claims(t@, config.jwt_secret@) matches Some(c) && c.sub@ == a.id && c.role@ == a.role),",
        "        r matches Ok(t) ==> (named_account(email, username) matches Some(a) && password_matches(password@, a.password_hash) && (token_claims(t@, config.jwt_secret@) matches Some(c) && c.sub@ == a.id && c.role@ == a.role)),",
        "parentheses around the second `matches` chain",
    ),
    (
        "        (r matches Ok(t) && token_claims(t@, config.jwt_secret@) matches Some(c) && c.role@ == admin_role()) ==> (email is None && username matches Some(u) && admin_on_file(u@) is Some),",
        "        (r matches Ok(t) && token_claims(t@, config.jwt_secret@) matches Some(c) && c.role@ == admin_role()) ==> (email is None && (username matches Some(u) && admin_on_file(u@) is Some)),",
        "parentheses around the `matches` chain on the right of &&",
    ),
    (
        "        (r matches Ok(t) && email is Some) ==> (token_claims(t@, config.jwt_secret@) matches Some(c) && c.role@ == customer_role()),",
        "        r matches Ok(t) ==> (email is Some ==> (token_claims(t@, config.jwt_secret@) matches Some(c) && c.role@ == customer_role())),",
        "(A and B) implies C, written as A implies (B implies C) so `t` stays in scope",
    ),
    (
        "        email is None && username matches Some(u) ==> r == Ok::<LookupTarget, LoginError>(LookupTarget::AdminByUsername(u)),",
        "        email is None ==> (username matches Some(u) ==> r == Ok::<LookupTarget, LoginError>(LookupTarget::AdminByUsername(u))),",
        "(A and B) implies C, written as A implies (B implies C)",
    ),
    (
        "        r matches Ok(c) && target is AdminByUsername ==> c.role@ == admin_role(),",
        "        r matches Ok(c) ==> (target is AdminByUsername ==> c.role@ == admin_role()),",
        "(A and B) implies C, written as A implies (B implies C) so `c` stays in scope",
    ),
    (
        "        r matches Ok(c) && target is CustomerByEmail ==> c.role@ == customer_role(),",
        "        r matches Ok(c) ==> (target is CustomerByEmail ==> c.role@ == customer_role()),",
        "(A and B) implies C, written as A implies (B implies C) so `c` stays in scope",
    ),
]

# Published lines that the model deliberately does not copy, each with its reason.
STUB_BODY_LINES = {
    "    bcrypt::verify(password, hash).map_err(|e| e.to_string())",
    "    let now = chrono::Utc::now();",
    '    let exp = now.checked_add_signed(chrono::Duration::hours(24)).expect("valid timestamp");',
    "    Expiry { now: now.timestamp() as usize, exp: exp.timestamp() as usize }",
    "    AppError::from(e)",
}
PROVED_FUNCTIONS = ["login_flow", "login_core", "issue_token", "lookup_target", "decide_login"]
REGION_START = "// ---------------- Published contract text (copied; see study.py fidelity check) ----------------"
REGION_END = "// ---------------- Helpers for the proved bodies (not part of the published contract) ----------------"
EXPECTED_ATTRIBUTES = [
    ("external_fn_specification", "ex_customer_find_by_email"),
    ("external_fn_specification", "ex_admin_find_by_username"),
    ("external_body", "check_password"),
    ("external_body", "expiry_from_now"),
    ("external_fn_specification", "ex_generate_token"),
    ("external_body", "database_error"),
]
FORBIDDEN = [r"\bassume\s*\(", r"\badmit\s*\(", r"assume_specification", r"#\[verifier\(",
             r"#\[verifier::external\]", r"exec_allows_no_decreases_clause", r"#!\[verifier"]

# ---------------------------------------------------------------- variants

DECIDE_BODY = """    match found {
        None => Err(LoginError::Unauthorized),
        Some(row) => match check_password(password, row.password_hash.as_str()) {
            Ok(true) => {
                let role = match target {
                    LookupTarget::AdminByUsername(_) => admin_role_text(),
                    LookupTarget::CustomerByEmail(_) => customer_role_text(),
                };
                Ok(IssuedClaims { sub: row.id, role })
            },
            Ok(false) => Err(LoginError::Unauthorized),
            Err(message) => Err(LoginError::UnreadableHash(message)),
        },
    }
"""
DECIDE_CHECKED_ARM = DECIDE_BODY.split("\n", 2)[2].rsplit("    }\n", 1)[0]
DECIDE_UNCHECKED_ARM = """        Some(row) => {
            let role = match target {
                LookupTarget::AdminByUsername(_) => admin_role_text(),
                LookupTarget::CustomerByEmail(_) => customer_role_text(),
            };
            Ok(IssuedClaims { sub: row.id, role })
        },
"""
LOOKUP_BODY = """    match email {
        Some(e) => Ok(LookupTarget::CustomerByEmail(e)),
        None => match username {
            Some(u) => Ok(LookupTarget::AdminByUsername(u)),
            None => Err(LoginError::MissingIdentity),
        },
    }
"""
LOOKUP_USERNAME_FIRST = """    match username {
        Some(u) => Ok(LookupTarget::AdminByUsername(u)),
        None => match email {
            Some(e) => Ok(LookupTarget::CustomerByEmail(e)),
            None => Err(LoginError::MissingIdentity),
        },
    }
"""
SIGN_WITH_EXPIRY = """            let expiry = expiry_from_now();
            let claims = Claims { sub: c.sub, role: c.role, exp: expiry.exp };
"""
DATABASE_ARM = "        Err(LoginError::Database(e)) => Err(database_error(e)),\n"
UNREADABLE_ARM = "            Err(message) => Err(LoginError::UnreadableHash(message)),\n"

REPAIR = [
    (
        "/// A clock reading for a token: `now` is the Unix time in seconds and `exp` the expiry written into the token.\n",
        "/// [Proposed addition, not published] The clock reading login signs with, when login looks.\n"
        "/// Left abstract: only `expiry_from_now`'s trusted contract says what it is.\n"
        "pub uninterp spec fn clock_at_login() -> usize;\n\n"
        "/// A clock reading for a token: `now` is the Unix time in seconds and `exp` the expiry written into the token.\n",
    ),
    (
        "        r.exp as int == r.now as int + 86_400,\n{\n",
        "        r.exp as int == r.now as int + 86_400,\n"
        "        // [Proposed addition] The reading is the clock when login looks.\n"
        "        r.now == clock_at_login(),\n{\n",
    ),
    (
        "        outcome matches Err(LoginError::Database(_)) ==> r matches Err(AppError::Internal(_)),\n{\n",
        "        outcome matches Err(LoginError::Database(_)) ==> r matches Err(AppError::Internal(_)),\n"
        "        // [Proposed addition] A token expires exactly 24 hours after the clock reading.\n"
        "        r matches Ok(t) ==> (token_claims(t@, config.jwt_secret@) matches Some(k) && k.exp as int == clock_at_login() as int + 86_400),\n{\n",
    ),
    (
        "        r matches Ok(t) ==> (email is Some ==> (token_claims(t@, config.jwt_secret@) matches Some(c) && c.role@ == customer_role())),\n{\n",
        "        r matches Ok(t) ==> (email is Some ==> (token_claims(t@, config.jwt_secret@) matches Some(c) && c.role@ == customer_role())),\n"
        "        // [Proposed addition] A token expires exactly 24 hours after the clock reading.\n"
        "        r matches Ok(t) ==> (token_claims(t@, config.jwt_secret@) matches Some(c) && c.exp as int == clock_at_login() as int + 86_400),\n{\n",
    ),
]

EXPIRED_ON_ARRIVAL = [(SIGN_WITH_EXPIRY, SIGN_WITH_EXPIRY.replace("exp: expiry.exp", "exp: expiry.now"))]
NEVER_EXPIRES = [(SIGN_WITH_EXPIRY, "            let claims = Claims { sub: c.sub, role: c.role, exp: usize::MAX };\n")]
SECRET_IN_500 = [(DATABASE_ARM, "        Err(LoginError::Database(e)) => Err(AppError::Internal(config.jwt_secret.clone())),\n")]
REPAIRED = ["expiry_from_now", "issue_token", "login_flow"]
UNREGROUP = [(model + "\n", published + "\n") for published, model, _ in REGROUPINGS]

VARIANTS = [
    {"name": "reference", "kind": "reference", "expect": "verified", "edits": [],
     "story": "Signs with the clock's 24-hour expiry, as the issue_token doc comment says."},
    {"name": "published-clauses-as-written", "kind": "front-end control", "expect": "front-end error",
     "edits": UNREGROUP, "allowed_changes": ["decide_login", "login_flow", "lookup_target"],
     "story": "The reference with the six regrouped clauses put back exactly as published."},
    {"name": "mutant-refuse-everyone", "kind": "published mutant", "expect": "rejected", "where": "decide_login",
     "edits": [(DECIDE_BODY, "    Err(LoginError::Unauthorized)\n")],
     "story": "PDD Kit mutant: always returns Err(LoginError::Unauthorized), whatever the password."},
    {"name": "mutant-skip-check", "kind": "published mutant", "expect": "rejected", "where": "decide_login",
     "edits": [(DECIDE_CHECKED_ARM, DECIDE_UNCHECKED_ARM)],
     "story": "PDD Kit mutant: issues claims for any row it finds, without asking check_password."},
    {"name": "mutant-username-first", "kind": "published mutant", "expect": "rejected", "where": "lookup_target",
     "edits": [(LOOKUP_BODY, LOOKUP_USERNAME_FIRST)],
     "story": "PDD Kit mutant: searches admins whenever a username is sent, even if an email was sent too."},
    {"name": "mutant-outage-as-401", "kind": "published mutant", "expect": "rejected", "where": "issue_token",
     "edits": [(DATABASE_ARM, "        Err(LoginError::Database(e)) => Err(AppError::Unauthorized),\n")],
     "story": "PDD Kit mutant: maps a failed lookup to AppError::Unauthorized instead of database_error."},
    {"name": "mutant-unreadable-as-401", "kind": "published mutant", "expect": "rejected", "where": "decide_login",
     "edits": [(UNREADABLE_ARM, "            Err(message) => Err(LoginError::Unauthorized),\n")],
     "story": "PDD Kit mutant: treats an error from check_password as a wrong password."},
    {"name": "counterworld-expired-on-arrival", "kind": "counterworld", "expect": "verified", "where": "issue_token",
     "edits": EXPIRED_ON_ARRIVAL,
     "story": "Writes the clock reading itself (expiry.now) as the expiry: every token is already expiring when issued."},
    {"name": "counterworld-never-expires", "kind": "counterworld", "expect": "verified", "where": "issue_token",
     "edits": NEVER_EXPIRES,
     "story": "Skips the clock and writes the largest possible expiry: tokens never expire."},
    {"name": "counterworld-secret-in-500", "kind": "counterworld", "expect": "verified", "where": "issue_token",
     "edits": SECRET_IN_500,
     "story": "Puts the JWT signing secret into the 500 message for a failed lookup."},
    {"name": "repaired-reference", "kind": "repaired contract", "expect": "verified", "where": "issue_token",
     "edits": REPAIR, "allowed_changes": REPAIRED,
     "story": "Proposed expiry clauses added; the reference body is unchanged."},
    {"name": "repaired-expired-on-arrival", "kind": "repaired contract", "expect": "rejected", "where": "issue_token",
     "edits": REPAIR + EXPIRED_ON_ARRIVAL, "allowed_changes": REPAIRED,
     "story": "Proposed expiry clauses added; the expired-on-arrival body."},
    {"name": "repaired-never-expires", "kind": "repaired contract", "expect": "rejected", "where": "issue_token",
     "edits": REPAIR + NEVER_EXPIRES, "allowed_changes": REPAIRED,
     "story": "Proposed expiry clauses added; the never-expires body."},
    {"name": "repaired-secret-in-500", "kind": "repaired contract", "expect": "verified", "where": "issue_token",
     "edits": REPAIR + SECRET_IN_500, "allowed_changes": REPAIRED,
     "story": "Proposed expiry clauses added; the secret-in-500 body (the repair is about expiry only)."},
]

# ---------------------------------------------------------------- helpers


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def scrub(text: str) -> str:
    """Replace the user's profile path so stored evidence does not reveal a username."""
    return text.replace(str(Path.home()), "%USERPROFILE%")


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def apply_edits(text: str, edits: list[tuple[str, str]]) -> str:
    for old, new in edits:
        count = text.count(old)
        if count != 1:
            raise ValueError(f"edit anchor found {count} times, expected once: {old[:80]!r}")
        text = text.replace(old, new)
    return text


def contract_blocks(text: str) -> dict[str, list[str]]:
    """Signature-to-body-brace block of every top-level `pub fn` / `pub async fn`, keyed by name."""
    lines = text.splitlines()
    blocks: dict[str, list[str]] = {}
    for index, line in enumerate(lines):
        match = re.match(r"pub (?:async )?fn (\w+)", line)
        if not match:
            continue
        end = index
        while lines[end] != "{" and not lines[end].endswith(" {"):
            end += 1
        blocks[match.group(1)] = lines[index:end + 1]
    return blocks


def normalize_published(line: str) -> str:
    for old, new in SUBSTITUTIONS:
        line = line.replace(old, new)
    for published, model, _ in REGROUPINGS:
        if line == published:
            return model
    return line


def verifier_attributes(text: str) -> list[tuple[str, str]]:
    lines = text.splitlines()
    found = []
    for index, line in enumerate(lines):
        match = re.match(r"\s*#\[verifier::(\w+)", line)
        if not match:
            continue
        name = next(re.search(r"fn (\w+)", later).group(1) for later in lines[index + 1:] if re.search(r"fn (\w+)", later))
        found.append((match.group(1), name))
    return found


def fidelity(published: str, model: str) -> dict:
    pub_lines = published.splitlines()
    model_lines = model.splitlines()
    verus_start = pub_lines.index("verus! {")
    type_start = verus_start + 1
    type_end = next(i for i, line in enumerate(pub_lines) if line.startswith("/// The customers row the database holds"))
    counts = {"verbatim": 0, "after_type_path_substitution": 0, "regrouped": 0, "blank": 0,
              "excluded_header_and_imports": 0, "excluded_host_type_specifications": 0,
              "excluded_trusted_body": 0, "excluded_proved_body_placeholder": 0}
    missing = []
    matched_model_lines = set()
    position = 0
    for number, line in enumerate(pub_lines, start=1):
        index = number - 1
        if not line.strip():
            counts["blank"] += 1
            continue
        if index < verus_start:
            counts["excluded_header_and_imports"] += 1
            continue
        if type_start <= index < type_end:
            counts["excluded_host_type_specifications"] += 1
            continue
        if line in STUB_BODY_LINES:
            counts["excluded_trusted_body"] += 1
            continue
        if line == "    unimplemented!()":
            counts["excluded_proved_body_placeholder"] += 1
            continue
        target = normalize_published(line)
        try:
            found = model_lines.index(target, position)
        except ValueError:
            missing.append({"published_line": number, "text": line})
            continue
        matched_model_lines.add(found)
        position = found + 1
        if target == line:
            counts["verbatim"] += 1
        elif any(line == published for published, _, _ in REGROUPINGS):
            counts["regrouped"] += 1
        else:
            counts["after_type_path_substitution"] += 1
    # Every model line in the published region must be a copied line or sit inside a function body.
    region_start = model_lines.index(REGION_START) + 1
    region_end = model_lines.index(REGION_END)
    extra = []
    in_body = False
    for index in range(region_start, region_end):
        line = model_lines[index]
        if line == "{":
            in_body = True
            continue
        if line == "}" and in_body:
            in_body = False
            continue
        if in_body or not line.strip() or index in matched_model_lines:
            continue
        extra.append({"model_line": index + 1, "text": line})
    pub_blocks = {name: [normalize_published(l) for l in block] for name, block in contract_blocks(published).items()}
    model_blocks = contract_blocks(model)
    block_mismatches = sorted(name for name, block in pub_blocks.items() if model_blocks.get(name) != block)
    attributes = verifier_attributes(model)
    forbidden = [pattern for pattern in FORBIDDEN if re.search(pattern, model)]
    passed = (not missing and not extra and not block_mismatches and attributes == EXPECTED_ATTRIBUTES and not forbidden
              and counts["regrouped"] == len(REGROUPINGS) and counts["excluded_proved_body_placeholder"] == len(PROVED_FUNCTIONS)
              and counts["excluded_trusted_body"] == len(STUB_BODY_LINES))
    return {
        "passed": passed,
        "published_lines": len(pub_lines),
        "counts": counts,
        "missing_published_lines": missing,
        "extra_model_lines_outside_bodies": extra,
        "contracts_compared": sorted(pub_blocks),
        "contract_block_mismatches": block_mismatches,
        "verifier_attributes": attributes,
        "verifier_attributes_expected": EXPECTED_ATTRIBUTES,
        "forbidden_patterns_found": forbidden,
        "regroupings": [{"published": p, "model": m, "why": w} for p, m, w in REGROUPINGS],
        "substitutions": SUBSTITUTIONS,
    }


def failure_locations(stderr: str, source_lines: list[str]) -> list[dict]:
    """Every source location Verus points at, with the line and the plain-English clause comment above it."""
    locations = []
    message = None
    for line in stderr.splitlines():
        error = re.match(r"(error|note|warning)(?:\[\w+\])?: (.+)", line)
        if error:
            message = error.group(2) if error.group(1) == "error" else None
            continue
        where = re.match(r"\s*(?:-->|:::)\s*(.+?):(\d+):(\d+)", line)
        if where and message:
            number = int(where.group(2))
            text = source_lines[number - 1].strip() if 0 < number <= len(source_lines) else ""
            comment = ""
            for back in range(number - 2, max(number - 4, -1), -1):
                candidate = source_lines[back].strip()
                if candidate.startswith("//"):
                    comment = candidate.lstrip("/ ").strip()
                    break
            locations.append({"message": message, "line": number, "source": text, "clause_comment": comment})
    return locations


def run_verus(verus: Path, env: dict, source: Path) -> dict:
    command = [str(verus), str(source), "--crate-type=lib", "--output-json", "--multiple-errors=20"]
    started = time.perf_counter()
    result = subprocess.run(command, env=env, capture_output=True, text=True, cwd=source.parent)
    elapsed = time.perf_counter() - started
    summary = None
    try:
        summary = json.loads(result.stdout).get("verification-results")
    except json.JSONDecodeError:
        pass
    return {"command": [Path(c).name if i < 2 else c for i, c in enumerate(command)], "exit_code": result.returncode,
            "seconds": round(elapsed, 2), "stdout": result.stdout, "stderr": result.stderr, "summary": summary}


def tamper_controls(published: str, model: str) -> list[dict]:
    """The fidelity check must fail when the copied contract is weakened or given an extra precondition."""
    controls = [
        ("weaken a decide_login clause",
         [("        found is None ==> r == Err::<IssuedClaims, LoginError>(LoginError::Unauthorized),\n",
           "        found is None ==> r is Err,\n")]),
        ("add a precondition to login_flow",
         [("pub async fn login_flow(pool: &SqlitePool, config: &Config, email: Option<String>, username: Option<String>, password: &str) -> (r: Result<String, AppError>)\n",
           "pub async fn login_flow(pool: &SqlitePool, config: &Config, email: Option<String>, username: Option<String>, password: &str) -> (r: Result<String, AppError>)\n    requires\n        false,\n")]),
        ("trust a proved function",
         [("pub fn decide_login(", "#[verifier::external_body]\npub fn decide_login(")]),
        ("add an extra declaration among the copied contract",
         [("/// Which table a login searches, and for which identifier.\n",
           "pub uninterp spec fn shortcut() -> bool;\n\n/// Which table a login searches, and for which identifier.\n")]),
        ("add an admitted lemma among the helpers",
         [("fn missing_identity_message() -> (r: String)\n",
           "proof fn shortcut()\n    ensures\n        false,\n{\n    admit();\n}\n\nfn missing_identity_message() -> (r: String)\n")]),
    ]
    outcomes = []
    for name, edits in controls:
        tampered = apply_edits(model, edits)
        outcomes.append({"control": name, "fidelity_passed": fidelity(published, tampered)["passed"]})
    return outcomes


def environment(verus: Path, env: dict) -> dict:
    version = subprocess.run([str(verus), "--version", "--output-json"], env=env, capture_output=True, text=True)
    try:
        verus_version = json.loads(version.stdout)
    except json.JSONDecodeError:
        verus_version = {"raw": version.stdout + version.stderr}
    hashes = {}
    for name in ["verus.exe", "rust_verify.exe", "z3.exe"]:
        path = verus.parent / name
        if path.exists():
            hashes[name] = sha256_file(path)
    return {"verus": verus_version, "binary_sha256": hashes, "python": sys.version, "platform": platform.platform(),
            "machine": platform.machine(), "processor_architecture": os.environ.get("PROCESSOR_ARCHITECTURE")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    parser.add_argument("--out", type=Path, default=HERE.parent / "evidence" / f"verus-login-{stamp}")
    parser.add_argument("--published", type=Path, default=DEFAULT_PUBLISHED)
    parser.add_argument("--verus-home", type=Path, default=DEFAULT_VERUS_HOME)
    args = parser.parse_args()

    # The hash is of the extracted text with LF line endings (Windows may store the cached copy with CRLF).
    published_bytes = args.published.read_bytes().replace(b"\r\n", b"\n")
    if sha256_bytes(published_bytes) != PUBLISHED_SHA256:
        print(f"published file hash (LF line endings) differs from {PUBLISHED_SHA256}; refusing to run", file=sys.stderr)
        return 2
    published = published_bytes.decode("utf-8")
    model = MODEL.read_text(encoding="utf-8")

    # Absolute, because Verus runs with the variant's folder as its working directory.
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    (out / "variants").mkdir()

    verus = args.verus_home / "verus-arm64-win" / "verus.exe"
    env = dict(os.environ, RUSTUP_HOME=str(args.verus_home / "rustup"), CARGO_HOME=str(args.verus_home / "cargo"))
    env["PATH"] = str(args.verus_home / "cargo" / "bin") + os.pathsep + env["PATH"]

    record = {
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "page": PAGE_URL,
        "asset": {"url": ASSET_URL, "sha256_at_extraction": ASSET_SHA256},
        "published_login_rs": {"path_outside_repo": scrub(str(args.published)), "sha256_lf": PUBLISHED_SHA256},
        "model": {"file": MODEL.name, "sha256": sha256_file(MODEL)},
        "harness": {"file": Path(__file__).name, "sha256": sha256_file(Path(__file__))},
        "environment": environment(verus, env),
    }
    record["fidelity"] = fidelity(published, model)
    record["fidelity_tamper_controls"] = tamper_controls(published, model)
    controls_ok = all(not control["fidelity_passed"] for control in record["fidelity_tamper_controls"])

    reference_blocks = contract_blocks(model)
    results = []
    for variant in VARIANTS:
        source_text = apply_edits(model, variant["edits"])
        path = out / "variants" / f"{variant['name']}.rs"
        path.write_bytes(source_text.encode("utf-8"))
        blocks = contract_blocks(source_text)
        changed_contracts = sorted(name for name in reference_blocks if blocks.get(name) != reference_blocks[name])
        contract_rule_ok = changed_contracts == sorted(variant.get("allowed_changes", []))
        clean = (verifier_attributes(source_text) == EXPECTED_ATTRIBUTES
                 and not any(re.search(pattern, source_text) for pattern in FORBIDDEN))
        run = run_verus(verus, env, path)
        (out / "variants" / f"{variant['name']}.stdout.json").write_text(scrub(run["stdout"]), encoding="utf-8")
        (out / "variants" / f"{variant['name']}.stderr.txt").write_text(scrub(run["stderr"]), encoding="utf-8")
        summary = run["summary"] or {}
        if run["exit_code"] == 0 and summary.get("success") is True and summary.get("errors") == 0:
            outcome = "verified"
        elif run["exit_code"] != 0 and summary.get("errors", 0) > 0 and not summary.get("encountered-vir-error"):
            outcome = "rejected"
        elif run["exit_code"] != 0 and not summary.get("errors"):
            outcome = "front-end error"
        else:
            outcome = "did not run cleanly"
        complaints = failure_locations(run["stderr"], source_text.splitlines())
        met = outcome == variant["expect"]
        if variant["kind"] == "front-end control":
            met = met and {c["source"] for c in complaints} == {p.strip() for p, _, _ in REGROUPINGS}
        if variant["kind"] == "repaired contract" and variant["expect"] == "rejected":
            met = met and bool(complaints) and all(c["clause_comment"].startswith("[Proposed addition]") for c in complaints)
        entry = {
            "name": variant["name"], "kind": variant["kind"], "where": variant.get("where"), "story": variant["story"],
            "expected": variant["expect"], "outcome": outcome, "met_expectation": met,
            "contracts_changed": changed_contracts, "contract_rule_ok": contract_rule_ok, "no_cheating_constructs": clean,
            "source_sha256": sha256_file(path), "exit_code": run["exit_code"], "seconds": run["seconds"],
            "verus_summary": summary, "complaints": complaints,
            "command": run["command"],
        }
        results.append(entry)
        print(f"{variant['name']:34s} expected {variant['expect']:8s} got {outcome:20s} "
              f"verified={summary.get('verified')} errors={summary.get('errors')} {run['seconds']}s")

    record["variants"] = results
    record["finished_utc"] = datetime.now(timezone.utc).isoformat()
    record["all_checks_passed"] = (record["fidelity"]["passed"] and controls_ok
                                   and all(r["met_expectation"] and r["contract_rule_ok"] and r["no_cheating_constructs"] for r in results))
    results_path = out / "results.json"
    results_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print("fidelity", "PASS" if record["fidelity"]["passed"] else "FAIL", record["fidelity"]["counts"])
    print("tamper controls caught", sum(not c["fidelity_passed"] for c in record["fidelity_tamper_controls"]),
          "of", len(record["fidelity_tamper_controls"]))
    print("all checks", "PASS" if record["all_checks_passed"] else "FAIL")
    print("results", scrub(str(results_path)), "sha256", sha256_file(results_path))
    return 0 if record["all_checks_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
