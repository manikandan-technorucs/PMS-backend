import asyncio
from app.core.database import SessionLocal
from app.models.automation import AutomationLog

def test():
    db = SessionLocal()
    logs = db.query(AutomationLog).all()
    for l in logs:
        print(f"Log ID: {l.id} | Status: {l.execution_status} | Error: {l.error_message}")

if __name__ == "__main__":
    test()
