from app.core.database import SessionLocal
from app.models.project import Project
from app.models.masters import Status

def check_project_statuses():
    db = SessionLocal()
    try:
        projects = db.query(Project).all()
        print(f"Total Projects: {len(projects)}")
        statuses = db.query(Status).all()
        status_map = {s.id: s.name for s in statuses}
        
        counts = {"Planning": 0, "Active": 0, "Completed": 0, "In Progress": 0, "Pending": 0, "None": 0}
        for p in projects:
            s_name = status_map.get(p.status_id, "None")
            counts[s_name] = counts.get(s_name, 0) + 1
            
        print("\nProject Counts by Status:")
        for s, c in counts.items():
            print(f"- {s}: {c}")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_project_statuses()
