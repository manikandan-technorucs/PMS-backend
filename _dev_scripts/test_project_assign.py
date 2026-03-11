from app.core.database import SessionLocal
from app.models.project import Project
from app.models.user import User
from app.services.project_service import add_user_to_project

def simulate_project_assignment():
    db = SessionLocal()
    try:
        # Get first project and first user
        project = db.query(Project).first()
        user = db.query(User).first()
        
        if not project or not user:
            print("No project or user found to test.")
            return

        print(f"Simulating assignment of User {user.email} to Project {project.name}...")
        
        # This should trigger the automation
        success = add_user_to_project(db, project.id, user.id)
        
        if success:
            print("Assignment function called successfully.")
        else:
            print("Assignment function returned False (maybe already assigned).")
            
    finally:
        db.close()

if __name__ == "__main__":
    simulate_project_assignment()
