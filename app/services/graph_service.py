"""
MS Graph Service — Azure Entra ID User Search with JIT Identity Provisioning

search_azure_users()
    Queries the Microsoft Graph /users endpoint with:
    - ConsistencyLevel: eventual  (mandatory for advanced $filter)
    - $count=true                 (mandatory alongside ConsistencyLevel)
    Without these two, Graph returns 403 Authorization_RequestDenied even
    when the SPN has User.Read.All.

_jit_upsert_user()
    Atomic identity sync: if a user returned by Graph is not yet in the
    local MySQL users table, upsert them inside a SQLAlchemy savepoint.
    Ensures referential integrity when assigning users found only in Entra.
"""

import msal
import requests
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.core.config import settings


# ── Token Acquisition ─────────────────────────────────────────────────────

def get_graph_token() -> str:
    """Acquires an app-only (client-credentials) token from Entra ID."""
    if not settings.AZURE_CLIENT_ID or not settings.AZURE_CLIENT_SECRET or not settings.AZURE_TENANT_ID:
        raise ValueError(
            "Azure SPN credentials are not configured. "
            "Set AZURE_TENANT_ID, AZURE_CLIENT_ID, and AZURE_CLIENT_SECRET in .env."
        )

    authority = f"https://login.microsoftonline.com/{settings.AZURE_TENANT_ID}"
    msal_app = msal.ConfidentialClientApplication(
        settings.AZURE_CLIENT_ID,
        authority=authority,
        client_credential=settings.AZURE_CLIENT_SECRET,
    )

    # Use cached token if available (MSAL handles expiry internally)
    result = msal_app.acquire_token_silent(
        ["https://graph.microsoft.com/.default"], account=None
    )
    if not result:
        result = msal_app.acquire_token_for_client(
            scopes=["https://graph.microsoft.com/.default"]
        )

    if "access_token" in result:
        return result["access_token"]

    raise Exception(
        f"Failed to acquire Graph token: {result.get('error_description', 'Unknown error')}"
    )


# ── JIT Identity Provisioning ─────────────────────────────────────────────

def _jit_upsert_user(db: Session, graph_user: Dict[str, Any]) -> None:
    """
    Just-In-Time Identity Sync: ensure a Microsoft Entra user exists in
    the local MySQL `users` table before they are assigned to a project/task.

    Execution model — savepoint (nested transaction):
      • Uses db.begin_nested() to create a database SAVEPOINT.
      • If any write fails, only this savepoint rolls back; the caller's
        outer transaction is preserved (referential integrity maintained).
      • The caller must call db.commit() to flush the savepoint to disk.

    Upsert logic:
      1. OID match   → sync stale displayName / mail fields.
      2. Email match → backfill missing o365_id (legacy user bridging).
      3. No match    → provision a minimal stub user from Graph claims.
    """
    from app.models.user import User
    from app.utils.ids import generate_public_id

    oid          = graph_user.get("id")
    mail         = graph_user.get("mail") or graph_user.get("userPrincipalName", "")
    display_name = graph_user.get("displayName", "")

    if not oid or not mail:
        return  # Cannot provision without both OID and mail — skip silently

    try:
        with db.begin_nested():  # SAVEPOINT — atomic, independent rollback
            # ── Case 1: OID already exists → sync stale display data ──────
            existing = db.query(User).filter(User.o365_id == oid).first()
            if existing:
                stale = (
                    existing.display_name != display_name
                    or existing.email != mail
                )
                if stale:
                    existing.display_name = display_name
                    existing.email        = mail
                return  # Savepoint committed on context-manager exit

            # ── Case 2: Email match → backfill missing OID (legacy bridge) ─
            existing_by_email = db.query(User).filter(User.email == mail).first()
            if existing_by_email:
                existing_by_email.o365_id     = oid
                existing_by_email.display_name = display_name
                existing_by_email.is_synced   = True
                return  # Savepoint committed

            # ── Case 3: No match → provision new stub from Graph claims ────
            name_parts = display_name.split(" ", 1)
            first_name = name_parts[0]
            last_name  = name_parts[1] if len(name_parts) > 1 else "User"

            db.add(User(
                public_id    = generate_public_id("USR-"),
                employee_id  = generate_public_id("EMP-"),
                o365_id      = oid,
                email        = mail,
                username     = mail.split("@")[0],
                first_name   = first_name,
                last_name    = last_name,
                display_name = display_name,
                is_synced    = True,
            ))
            # Savepoint committed on context-manager exit

    except Exception as exc:
        # Savepoint already rolled back by context manager on exception.
        # Log but do not re-raise — search results are still valid.
        print(f"[JIT UPSERT WARNING] Could not provision user {mail}: {exc}")


# ── Primary Search Function ───────────────────────────────────────────────

def search_azure_users(
    query: str,
    db: Optional[Session] = None,
) -> List[Dict[str, Any]]:
    """
    Search Microsoft Entra ID for users by displayName, mail, or UPN.

    Root-cause fix for 403 Authorization_RequestDenied
    ───────────────────────────────────────────────────
    MS Graph advanced $filter queries (startswith on non-indexed attributes)
    require TWO prerequisites to be satisfied simultaneously:

      1. ConsistencyLevel: eventual  — signals the query engine to use the
         eventually-consistent index store (required for $filter + $count).
      2. $count=true in the query string — without this parameter, Graph
         ignores ConsistencyLevel and returns 403 regardless of permissions.

    Both must be present. Either alone is insufficient.

    JIT Provisioning
    ────────────────
    If a db session is supplied, each returned Graph user is upserted into
    the local MySQL users table (inside a savepoint) so that subsequent
    project/task assignment calls never encounter a missing FK reference.

    Parameters
    ----------
    query : str
        Partial name or email prefix (minimum 2 chars enforced at endpoint).
    db    : Session | None
        Active SQLAlchemy session for JIT provisioning. Pass None to skip sync
        (e.g. from background tasks that do not have a request-scoped session).

    Returns
    -------
    List of dicts with keys: id, displayName, mail
    """
    token = get_graph_token()

    # ConsistencyLevel: eventual — REQUIRED for advanced $filter + $count
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json",
        "ConsistencyLevel": "eventual",
    }

    # Sanitise input: escape single quotes to prevent OData injection
    safe_query = query.replace("'", "''")

    # Bounded prefix search (startswith) — prevents full directory enumeration
    odata_filter = (
        f"startswith(displayName,'{safe_query}') or "
        f"startswith(mail,'{safe_query}') or "
        f"startswith(userPrincipalName,'{safe_query}')"
    )

    # $count=true is MANDATORY when ConsistencyLevel is set —
    # Graph rejects the request with 400 if $count is absent.
    url = (
        "https://graph.microsoft.com/v1.0/users"
        f"?$filter={odata_filter}"
        f"&$select=id,displayName,mail"
        f"&$top=10"
        f"&$count=true"
    )

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"[GRAPH API ERROR] {response.status_code} — {response.text}")
        raise Exception(
            f"Graph API Error {response.status_code}: {response.text}"
        )

    users: List[Dict[str, Any]] = response.json().get("value", [])

    # ── JIT Identity Provisioning ────────────────────────────────────────
    # Upserts returned Graph users into local MySQL inside individual
    # savepoints. A failure in one upsert does not block the others.
    if db is not None and users:
        try:
            for graph_user in users:
                _jit_upsert_user(db, graph_user)
            db.commit()
        except Exception as exc:
            db.rollback()
            print(f"[JIT SYNC WARNING] Batch commit failed, rolled back: {exc}")
            # Non-fatal: return Graph results even if local sync fails

    return users
