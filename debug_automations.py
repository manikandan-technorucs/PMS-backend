from app.core.database import SessionLocal
from app.models.automation import AutomationRule, AutomationLog, EmailTemplate
import json

def check_automations():
    db = SessionLocal()
    try:
        rules = db.query(AutomationRule).all()
        print(f"Total Rules: {len(rules)}")
        for r in rules:
            print(f"- Rule ID: {r.id}, Trigger: {r.trigger_event}, Active: {r.is_active}, Template ID: {r.template_id}")
            
        templates = db.query(EmailTemplate).all()
        print(f"\nEmail Templates: {len(templates)}")
        for t in templates:
            print(f"- Template ID: {t.id}, Name: {t.name}")
            
        logs = db.query(AutomationLog).order_by(AutomationLog.triggered_at.desc()).limit(10).all()
        print(f"\nRecent Logs (Total: {db.query(AutomationLog).count()}):")
        for l in logs:
            print(f"- Log ID: {l.id}, Rule ID: {l.rule_id}, Status: {l.execution_status}, Error: {l.error_message}, Key: {l.idempotency_key}")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_automations()
