from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.masters import Department, Location, UserStatus, Skill, Status, Priority
from app.models.roles import Role
from app.models import *  

def seed_data(db: Session):
    Base.metadata.create_all(bind=engine)
    
    if db.query(Department).count() == 0:
        departments = [
            Department(name="Engineering"),
            Department(name="Product"),
            Department(name="Sales"),
            Department(name="HR"),
            Department(name="QA"),
        ]
        db.add_all(departments)

    if db.query(Location).count() == 0:
        locations = [
            Location(name="Chennai"),
            Location(name="Bangalore"),
            Location(name="Remote"),
        ]
        db.add_all(locations)

    if db.query(UserStatus).count() == 0:
        statuses = [
            UserStatus(name="Active"),
            UserStatus(name="Inactive"),
            UserStatus(name="Onboarding"),
        ]
        db.add_all(statuses)

    if db.query(Status).count() == 0:
        core_statuses = [
            Status(name="Active"),
            Status(name="In Progress"),
            Status(name="Completed"),
            Status(name="Pending"),
        ]
        db.add_all(core_statuses)

    if db.query(Priority).count() == 0:
        priorities = [
            Priority(name="Low"),
            Priority(name="Medium"),
            Priority(name="High"),
            Priority(name="Critical"),
        ]
        db.add_all(priorities)

    all_perms_except_user_mutations = {
        "proj-view": True, "proj-create": True, "proj-edit": True, "proj-delete": True,
        "task-view": True, "task-create": True, "task-edit": True, "task-delete": True,
        "user-view": True, "user-create": False, "user-edit": False, "user-delete": False,
        "report-view": True, "report-export": True,
        "settings-view": True, "settings-edit": True
    }

    team_lead_perms = {
        "user-view": True,
        "task-view": True, "task-create": True, "task-edit": True, "task-delete": True
    }

    if db.query(Role).count() == 0:
        roles = [
            Role(name="Super Admin", permissions=all_perms_except_user_mutations),
            Role(name="Manager", permissions=all_perms_except_user_mutations),
            Role(name="Team Lead", permissions=team_lead_perms),
            Role(name="Employee", permissions={}),
        ]
        db.add_all(roles)

    if db.query(Skill).count() == 0:
        skills = [
            Skill(name="React"),
            Skill(name="Python"),
            Skill(name="FastAPI"),
            Skill(name="UI/UX Design"),
            Skill(name="DevOps"),
            Skill(name="Project Management"),
            Skill(name="Data Analytics"),
        ]
        db.add_all(skills)

    db.commit()
    print("Database seeding completed.")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()
