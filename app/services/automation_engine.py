from celery import shared_task
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.automation import AutomationRule, AutomationLog, EmailTemplate
from app.services.email_service import EmailService
from jinja2 import Environment, BaseLoader, StrictUndefined, TemplateError
import logging
from datetime import datetime, timezone
import json
from kombu.exceptions import OperationalError

logger = logging.getLogger(__name__)

# Security: strict undefined prevents silently ignoring missing variables
jinja_env = Environment(loader=BaseLoader(), undefined=StrictUndefined)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_automation_rule(self, rule_id: int, payload: dict, to_email: str, idempotency_key: str):
    """
    Celery task to execute an email automation. Features:
    - Retries (Max 3, backing off)
    - Idempotency protection (DB unique constraint)
    - Jinja2 Template rendering
    """
    db: Session = SessionLocal()
    try:
        
        existing_log = db.query(AutomationLog).filter(AutomationLog.idempotency_key == idempotency_key).first()
        
        if existing_log:
            if existing_log.execution_status == "SUCCESS":
                logger.info(f"Idempotent task skipped. Key: {idempotency_key}")
                return "SKIPPED_IDEMPOTENT"
            
            log_entry = existing_log
        else:
            # Create PENDING log
            log_entry = AutomationLog(
                rule_id=rule_id,
                execution_status="PENDING",
                idempotency_key=idempotency_key
            )
            db.add(log_entry)
            db.commit()
            db.refresh(log_entry)

        # 2. Fetch Rule and Template
        rule = db.query(AutomationRule).filter(AutomationRule.id == rule_id).first()
        if not rule or not rule.is_active:
            raise ValueError(f"Rule {rule_id} is inactive or missing")
            
        template = rule.template
        if not template or not template.is_active:
            raise ValueError(f"Template for rule {rule_id} is inactive or missing")

        # 3. Render Template via Jinja2
        try:
            subject_temp = jinja_env.from_string(template.subject)
            rendered_subject = subject_temp.render(**payload)
            
            body_temp = jinja_env.from_string(template.body_html)
            rendered_body = body_temp.render(**payload)
            
            rendered_text = None
            if template.body_text:
                text_temp = jinja_env.from_string(template.body_text)
                rendered_text = text_temp.render(**payload)
                
        except TemplateError as e:
            raise ValueError(f"Template rendering failed: {str(e)}")

        # 4. Dispatch Email
        success = EmailService.send_email(
            to_email=to_email,
            subject=rendered_subject,
            body_html=rendered_body,
            body_text=rendered_text
        )

        if not success:
            raise Exception("EmailService returned False")

        # 5. Success
        log_entry.execution_status = "SUCCESS"
        log_entry.completed_at = datetime.now(timezone.utc)
        log_entry.error_message = None
        db.commit()
        return "SUCCESS"

    except Exception as exc:
        db.rollback()
        
        # Log failure
        if 'log_entry' in locals():
            log_entry.execution_status = "FAILED"
            log_entry.error_message = str(exc)
            log_entry.completed_at = datetime.now(timezone.utc)
            db.commit()
            
        logger.error(f"Rule {rule_id} failed: {str(exc)}")
        # Trigger Celery retry with exponential backoff
        countdown = 60 * (2 ** self.request.retries) 
        raise self.retry(exc=exc, countdown=countdown)
    finally:
        db.close()

def execute_automation_event(db: Session, event_name: str, payload: dict, email_recipient: str, entity_id: str, tenant_id: str = None):
    """
    Entrypoint called by FastAPI routes (e.g. after Task is created).
    """
    query = db.query(AutomationRule).filter(AutomationRule.trigger_event == event_name, AutomationRule.is_active == True)
    if tenant_id:
        query = query.filter(AutomationRule.tenant_id == tenant_id)
        
    rules = query.all()
    
    for rule in rules:
        # Basic conditions evaluation (if conditions_json is set in the rule)
        if rule.conditions_json:
            conditions = rule.conditions_json if isinstance(rule.conditions_json, dict) else json.loads(rule.conditions_json)
            match = all(payload.get(k) == v for k, v in conditions.items())
            if not match:
                continue # Skip if payload doesn't match rule conditions

        # Generate deterministic idempotency key
        idempotency_key = f"evt_{event_name}_rule_{rule.id}_entity_{entity_id}"
        
        # Dispatch to Celery background worker
        try:
            process_automation_rule.delay(
                rule_id=rule.id,
                payload=payload,
                to_email=email_recipient,
                idempotency_key=idempotency_key
            )
        except OperationalError:
            logger.warning("Celery broker (Redis) is unreachable. Falling back to synchronous execution.")
            # Execute synchronously as a fallback
            try:
                # We essentially replicate the behavior of the bound task locally
                # Normally 'self' is passed by Celery, but since we are calling it directly 
                # we pass a dummy 'self' or None, since 'self.request.retries' won't work.
                # Here we just pass None for self if the task function allows it, however it has bind=True.
                # Actually, calling a bound shared_task synchronously requires .apply() or calling the underlying fn.
                
                # To bypass the bind 'self' issue, we can just call process_automation_rule directly 
                # passing None or a mock object for self. But it's safer to use .apply() which 
                # executes it synchronously using Celery's machinery, or just passing a mock.
                # However, for simplicity let's rely on .apply()
                process_automation_rule.apply(
                    kwargs={
                        "rule_id": rule.id,
                        "payload": payload,
                        "to_email": email_recipient,
                        "idempotency_key": idempotency_key
                    }
                )
            except Exception as fe:
                logger.error(f"Fallback synchronous execution also failed: {fe}")
