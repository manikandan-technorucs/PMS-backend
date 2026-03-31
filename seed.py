from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.masters import Department, UserStatus, Skill, Status, Priority
from app.models.roles import Role

def seed_data(db: Session):
    # 1. Ensure tables are created
    Base.metadata.create_all(bind=engine)

    # 2. Seed Departments
    if db.query(Department).count() == 0:
        departments = ["Engineering", "Marketing", "O365", "Sales", "Business Analyst"]
        db.add_all([Department(name=name) for name in departments])

    # 3. Seed User Statuses
    if db.query(UserStatus).count() == 0:
        user_statuses = ["Active", "Inactive", "Pending", "Onboarding", "On Leave"]
        db.add_all([UserStatus(name=name) for name in user_statuses])

    # 4. Seed Entity Statuses (Project/Task/Issue)
    if db.query(Status).count() == 0:
        entity_statuses = ["Planning", "Open", "In Progress", "Completed", "On Hold", "Closed","Re-open"]
        db.add_all([Status(name=name) for name in entity_statuses])

    # 5. Seed Priorities
    if db.query(Priority).count() == 0:
        priorities = ["Low", "Medium", "High", "Critical"]
        db.add_all([Priority(name=name) for name in priorities])

    # 6. Seed Roles with Permissions
    # Check if we have the correct canonical roles
    canonical_roles = ["Admin", "Project Manager", "Team Lead", "Employee"]
    existing_roles = {r.name for r in db.query(Role).all()}
    
    missing_roles = [name for name in canonical_roles if name not in existing_roles]
    if missing_roles:
        new_roles = [Role(name=name, permissions={}) for name in missing_roles]
        db.add_all(new_roles)

    # 7. Seed Skills
    if db.query(Skill).count() == 0:
        skills = ["React", "Python", "FastAPI", "UI/UX Design", "Node.js", ".NET", "DevOps", "Project Management", "Data Analytics"]
        db.add_all([Skill(name=name) for name in skills])

    db.commit() # Initial commit for masters/roles
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()