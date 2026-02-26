from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.masters import Department, Location, UserStatus, Skill
from app.models.roles import Role
from app.models import *  

def seed_data(db: Session):
    Base.metadata.create_all(bind=engine)
    
    if db.query(Department).count() > 0:
        print("Database already seeded. Skipping.")
        return

    departments = [
        Department(name="Engineering"),
        Department(name="Product"),
        Department(name="Sales"),
        Department(name="HR"),
        Department(name="QA"),
    ]
    db.add_all(departments)

    locations = [
        Location(name="Chennai"),
        Location(name="Bangalore"),
        Location(name="Remote"),
    ]
    db.add_all(locations)

    statuses = [
        UserStatus(name="Active"),
        UserStatus(name="Inactive"),
        UserStatus(name="Onboarding"),
    ]
    db.add_all(statuses)

    roles = [
        Role(name="Super Admin", permissions={"proj-view": True, "proj-create": True, "task-view": True, "user-view": True}),
        Role(name="Manager", permissions={"proj-view": True, "task-view": True, "user-view": False}),
        Role(name="Team Lead", permissions={"proj-view": False, "task-view": True}),
        Role(name="Employee", permissions={}),
    ]
    db.add_all(roles)

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
