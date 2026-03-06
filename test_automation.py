from app.core.database import SessionLocal
from app.services.automation_engine import execute_automation_event

def test_automation():
    db = SessionLocal()
    payload = {
        "task_name": "Test Email Automation Task",
        "assigned_user": "John Doe",
        "project_name": "Zoho Replica"
    }
    
    print("Executing automation event 'TASK_ASSIGNED'...")
    execute_automation_event(
        db=db,
        event_name="TASK_ASSIGNED",
        payload=payload,
        email_recipient="test@example.com",
        entity_id="test_task_123"
    )
    print("Event dispatched. Check Celery logs for processing output.")
    
if __name__ == "__main__":
    test_automation()
