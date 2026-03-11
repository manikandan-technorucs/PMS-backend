import asyncio
from app.core.database import SessionLocal
from app.models.automation import AutomationRule

def check():
    db = SessionLocal()
    rules = db.query(AutomationRule).all()
    if not rules:
        print("No active rules in the database!")
    for r in rules:
        print(f"Rule ID: {r.id} | Event: {r.trigger_event} | Active: {r.is_active} | Conditions: {r.conditions_json}")

if __name__ == "__main__":
    check()
