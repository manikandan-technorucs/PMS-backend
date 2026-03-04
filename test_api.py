import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.db.database import SessionLocal
from app.services.timelog_service import get_timelogs
from app.schemas.timelog import TimeLogResponse

db = SessionLocal()
logs = get_timelogs(db)
print(f"Found {len(logs)} logs")
for log in logs[:2]:
    response_model = TimeLogResponse.model_validate(log)
    data = response_model.model_dump()
    print(f"Log ID: {data['id']}")
    print(f"Task: {data.get('task')}")
    if data.get('task'):
        print(f"Task Project: {data['task'].get('project')}")

db.close()
