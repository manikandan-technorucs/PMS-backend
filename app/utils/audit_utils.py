"""
Audit Utilities — Transactional Header-Detail Audit Logging

Exports
-------
capture_audit_details(old_obj, new_data_dict)
    Diff helper: compares ORM object attributes against a mutation dict
    and returns a list of changed-field descriptors.

write_audit(db, actor_id, action_type, resource_name, resource_id, record_id, details)
    Atomically writes one AuditLogs header row + N AuditLogDetails rows
    using a SQLAlchemy savepoint (db.begin_nested()).

    Savepoint semantics (referential integrity guarantee)
    ─────────────────────────────────────────────────────
    • db.begin_nested() issues a database SAVEPOINT before inserting the
      header row.
    • db.flush() inside the savepoint populates the auto-generated header
      PK so detail rows can reference it (via AuditLogId FK).
    • If ANY detail INSERT fails (e.g. FK violation, column overflow), the
      entire savepoint — header + all details — rolls back atomically.
    • The outer caller transaction is NOT affected: business data already
      flushed to the session survives the audit failure.
    • Caller must call db.commit() after write_audit() to persist everything.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import uuid

from sqlalchemy.orm import Session


# ── Field-Level Diff Helper ───────────────────────────────────────────────

def capture_audit_details(
    old_obj: Any,
    new_data_dict: Dict[str, Any],
) -> List[Dict[str, Optional[str]]]:
    """
    Compare the current attribute values of *old_obj* with the key/value
    pairs in *new_data_dict*.

    For every field whose value has changed, returns a dict with:
      - field_name : the attribute name
      - old_value  : serialised string of the previous value (or None)
      - new_value  : serialised string of the incoming value (or None)

    Both values are stored as strings for TEXT column compatibility.
    Non-mutated fields are silently skipped.
    """
    changes: List[Dict[str, Optional[str]]] = []

    for field, new_value in new_data_dict.items():
        old_value = getattr(old_obj, field, None)

        # Normalise both sides to strings for reliable comparison
        old_str = str(old_value) if old_value is not None else None
        new_str = str(new_value) if new_value is not None else None

        if old_str != new_str:
            changes.append(
                {
                    "field_name": field,
                    "old_value":  old_str,
                    "new_value":  new_str,
                }
            )

    return changes


# ── Transactional Audit Writer ────────────────────────────────────────────

def write_audit(
    db:            Session,
    actor_id:      Optional[str],
    action_type:   str,
    resource_name: str,
    resource_id:   int,
    record_id:     int,
    details:       Optional[List[Dict[str, Optional[str]]]] = None,
) -> None:
    """
    Atomically write one AuditLogs (header) row and optional AuditLogDetails
    (detail) rows inside a SQLAlchemy savepoint.

    Transactional Pattern — db.begin_nested()
    ──────────────────────────────────────────
    The savepoint wraps both the header INSERT and all detail INSERTs as a
    single atomic unit:

        outer session transaction
        └── SAVEPOINT write_audit
            ├── INSERT AuditLogs          → generates audit_log.ID
            ├── db.flush()                → resolves ID within savepoint
            └── INSERT AuditLogDetails × N

    If any detail INSERT raises (FK mismatch, value overflow, etc.), the
    SAVEPOINT ROLLBACK fires automatically via the context-manager __exit__,
    removing the header row too — preventing orphaned header records.
    The outer session is unaffected; caller can still db.commit() its changes.

    Parameters
    ----------
    db            : Active SQLAlchemy session (request-scoped).
    actor_id      : Microsoft OID (UUID string) of the acting user, or None
                    (falls back to the nil UUID — representing the "system").
    action_type   : Verb label — CREATE | UPDATE | DELETE | ASSIGN | REMOVE
                    (first word is mapped to an integer code for AuditLogs.Action).
    resource_name : Entity table name, e.g. "projects", "tasks" (max 250 chars).
    resource_id   : Project-context id for timeline filtering per project.
    record_id     : PK of the specific row that was acted on.
    details       : List of dicts with keys field_name, old_value, new_value.
                    Pass [] or None if no field-level diff is needed.
    """
    from app.models.audit import AuditLogs, AuditLogDetails

    # ── Action Code Mapping ───────────────────────────────────────────────
    action_map = {
        "CREATE": 1,
        "UPDATE": 2,
        "DELETE": 3,
        "ASSIGN": 4,
        "REMOVE": 5,
    }
    # Normalise compound verbs (e.g. "ASSIGN_TO_PROJECT" → "ASSIGN" → 4)
    action_verb = str(action_type).upper().split("_")[0]
    action_int  = action_map.get(action_verb, 5)

    # ── Actor UUID Resolution ─────────────────────────────────────────────
    try:
        performed_by = (
            uuid.UUID(actor_id)
            if actor_id and actor_id != "system"
            else uuid.UUID(int=0)       # Nil UUID for system-initiated actions
        )
    except (ValueError, AttributeError):
        performed_by = uuid.UUID(int=0)

    # ── Savepoint: Atomic Header + Detail Writes ──────────────────────────
    # Any exception raised inside this block triggers SAVEPOINT ROLLBACK.
    # The outer transaction is preserved for the caller to commit or roll back.
    with db.begin_nested():

        # ① Header row — establishes the AuditLogs.ID anchor
        audit_log = AuditLogs(
            TableName     = resource_name[:250],
            Action        = action_int,
            PerformedBy   = performed_by,
            PerformedOn   = datetime.now(timezone.utc).replace(tzinfo=None),  # naive UTC
            TransactionId = uuid.uuid4(),
            Comments      = f"Action: {action_type} on Record ID: {record_id}",
            ModuleName    = "System",
        )
        db.add(audit_log)

        # ② Flush within savepoint to resolve the auto-generated PK.
        #    Without this, AuditLogDetails.AuditLogId would be None (IntegrityError).
        db.flush()

        # ③ Detail rows — one per changed field
        if details:
            db.add_all([
                AuditLogDetails(
                    AuditLogId = audit_log.ID,
                    FieldName  = str(d.get("field_name", ""))[:250],
                    OldValue   = str(d["old_value"]) if d.get("old_value") is not None else None,
                    NewValue   = str(d["new_value"]) if d.get("new_value") is not None else None,
                    ValueType  = 1,     # 1 = plain text
                )
                for d in details
            ])

    # Savepoint is committed here (RELEASE SAVEPOINT).
    # Caller is responsible for the outer db.commit().
