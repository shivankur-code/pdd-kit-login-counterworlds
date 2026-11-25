//! Verus model of the login contract PDD Kit published for its Pet Store example:
//! verified/src/login.rs as rendered at https://githubnext.com/projects/pdd-kit/.
//! Every contract line below the host stand-ins is copied from that file; check_fidelity.py
//! re-extracts the published file and checks the copy line by line.
//! Host types are minimal stand-ins because the backend crate is not public, and trusted bodies
//! are stubs: this file is verified, never run. The published page leaves the five proved
//! functions as unimplemented!(); the bodies here follow its flowchart.

#![allow(unused_imports, dead_code, unused_variables)]
use vstd::prelude::*;
use vstd::string::*;

verus! {

// ---------------- Host stand-ins (not published) ----------------

/// Stand-in for sqlx::SqlitePool, opaque to the proof as in the published file.
pub struct SqlitePool {}

/// Stand-in for sqlx::Error, opaque to the proof as in the published file.
pub struct SqlxError {}

pub struct Customer {
    pub id: String,
    pub password_hash: String,
}

pub struct Admin {
    pub id: String,
    pub password_hash: String,
}

pub struct Config {
    pub jwt_secret: String,
}

/// A token's claims (`sub`, `role`, `exp`), the three fields the published comment lists.
pub struct Claims {
    pub sub: String,
    pub role: String,
    pub exp: usize,
}

/// The app's HTTP error (400, 401, 403, 404, 500).
pub enum AppError {
    BadRequest(String),
    Unauthorized,
    Forbidden,
    NotFound,
    Internal(String),
}

// ---------------- Published contract text (copied; see study.py fidelity check) ----------------

//@published 50-174
    unimplemented!()
//@published 176-192
    unimplemented!()
//@published 196-221
    unimplemented!()
//@published 223-280
    let outcome = login_core(pool, email, username, password).await;
    issue_token(outcome, config)
//@published 282-305
    match lookup_target(email, username) {
        Err(refusal) => Err(refusal),
        Ok(target) => {
            let looked_up: Result<Option<AccountRow>, SqlxError> = match &target {
                LookupTarget::CustomerByEmail(e) => match Customer::find_by_email(pool, e.as_str()).await {
                    Ok(Some(c)) => Ok(Some(AccountRow { id: c.id, password_hash: c.password_hash })),
                    Ok(None) => Ok(None),
                    Err(err) => Err(err),
                },
                LookupTarget::AdminByUsername(u) => match Admin::find_by_username(pool, u.as_str()).await {
                    Ok(Some(a)) => Ok(Some(AccountRow { id: a.id, password_hash: a.password_hash })),
                    Ok(None) => Ok(None),
                    Err(err) => Err(err),
                },
            };
            match looked_up {
                Err(err) => Err(LoginError::Database(err)),
                Ok(found) => decide_login(&target, found, password),
            }
        },
    }
//@published 307-325
    match outcome {
        Ok(c) => {
            let expiry = expiry_from_now();
            let claims = Claims { sub: c.sub, role: c.role, exp: expiry.exp };
            generate_token(&claims, config)
        },
        Err(LoginError::MissingIdentity) => Err(AppError::BadRequest(missing_identity_message())),
        Err(LoginError::Unauthorized) => Err(AppError::Unauthorized),
        Err(LoginError::UnreadableHash(m)) => Err(AppError::Internal(m)),
        Err(LoginError::Database(e)) => Err(database_error(e)),
    }
//@published 327-339
    match email {
        Some(e) => Ok(LookupTarget::CustomerByEmail(e)),
        None => match username {
            Some(u) => Ok(LookupTarget::AdminByUsername(u)),
            None => Err(LoginError::MissingIdentity),
        },
    }
//@published 341-364
    match found {
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
//@published 366-367
// ---------------- Helpers for the proved bodies (not part of the published contract) ----------------

fn missing_identity_message() -> (r: String)
    ensures
        r@ == missing_identity_text(),
{
    String::from_str("Either email or username is required")
}

fn admin_role_text() -> (r: String)
    ensures
        r@ == admin_role(),
{
    let mut s = String::new();
    s.push('a');
    s.push('d');
    s.push('m');
    s.push('i');
    s.push('n');
    assert(s@ =~= admin_role());
    s
}

fn customer_role_text() -> (r: String)
    ensures
        r@ == customer_role(),
{
    let mut s = String::new();
    s.push('c');
    s.push('u');
    s.push('s');
    s.push('t');
    s.push('o');
    s.push('m');
    s.push('e');
    s.push('r');
    assert(s@ =~= customer_role());
    s
}

} // verus!

// ---------------- Host stand-ins outside Verus (never run) ----------------

impl Customer {
    pub async fn find_by_email(_pool: &SqlitePool, _email: &str) -> Result<Option<Customer>, SqlxError> {
        unimplemented!("host stand-in: verified, never run")
    }
}

impl Admin {
    pub async fn find_by_username(_pool: &SqlitePool, _username: &str) -> Result<Option<Admin>, SqlxError> {
        unimplemented!("host stand-in: verified, never run")
    }
}

pub fn generate_token(_claims: &Claims, _config: &Config) -> Result<String, AppError> {
    unimplemented!("host stand-in: verified, never run")
}
