"""
Automation Engine — Event-driven automation system.

This module records automation events to the database.
Email notifications are handled externally via Power Automate 
(which polls or receives webhooks for new automation log entries).
"""
from sqlalchemy.orm import Session
from app.models.automation import AutomationRule, AutomationLog
import logging
from datetime import datetime, timezone
import json

logger = logging.getLogger(__name__)


def execute_automation_event(
    db: Session,
    event_name: str,
    payload: dict,
    email_recipient: str,
    entity_id: str,
    tenant_id: str = None
):
    """
    Entrypoint called by FastAPI services (e.g. after Task is created).
    
    Instead of sending emails directly, this function:
    1. Finds matching active automation rules for the event
    2. Evaluates rule conditions against the payload
    3. Logs the event to the automation_logs table with status 'PENDING'
    
    Power Automate can then:
    - Poll the /api/v1/automations/{rule_id}/logs endpoint for PENDING logs
    - Or receive a webhook (if configured) to process and send emails
    """
    query = db.query(AutomationRule).filter(
        AutomationRule.trigger_event == event_name,
        AutomationRule.is_active == True
    )
    if tenant_id:
        query = query.filter(AutomationRule.tenant_id == tenant_id)
        
    rules = query.all()
    
    for rule in rules:
        # Evaluate conditions (if any)
        if rule.conditions_json:
            conditions = (
                rule.conditions_json 
                if isinstance(rule.conditions_json, dict) 
                else json.loads(rule.conditions_json)
            )
            match = all(payload.get(k) == v for k, v in conditions.items())
            if not match:
                continue  # Skip if payload doesn't match rule conditions

        # Generate deterministic idempotency key
        idempotency_key = f"evt_{event_name}_rule_{rule.id}_entity_{entity_id}"
        
        try:
            # Check for existing log (idempotency)
            existing_log = db.query(AutomationLog).filter(
                AutomationLog.idempotency_key == idempotency_key
            ).first()
            
            if existing_log:
                logger.info(f"Event already logged. Key: {idempotency_key}")
                continue
            
            # Create log entry with PENDING status for Power Automate to pick up
            log_entry = AutomationLog(
                rule_id=rule.id,
                execution_status="PENDING",
                idempotency_key=idempotency_key,
                error_message=json.dumps({
                    "event": event_name,
                    "payload": payload,
                    "recipient": email_recipient
                })  # Store event data in error_message field for Power Automate to read
            )
            db.add(log_entry)
            db.commit()
            
            logger.info(
                f"Automation event logged: {event_name} → Rule {rule.id} "
                f"(recipient: {email_recipient})"
            )
            
        except Exception as exc:
            db.rollback()
            logger.error(f"Failed to log automation event for rule {rule.id}: {exc}")
