from sqlalchemy.orm import Session
from app.models.masters import Department, Location, UserStatus, Skill
from app.models.roles import Role

def get_departments(db: Session):
    return db.query(Department).all()

def get_locations(db: Session):
    return db.query(Location).all()

def get_statuses(db: Session):
    return db.query(UserStatus).all()

def get_roles(db: Session):
    return db.query(Role).all()

def get_role(db: Session, role_id: int):
    return db.query(Role).filter(Role.id == role_id).first()

def create_role(db: Session, role: dict):
    db_role = Role(**role)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def update_role(db: Session, role_id: int, role: dict):
    db_role = db.query(Role).filter(Role.id == role_id).first()
    if db_role:
        for key, value in role.items():
            setattr(db_role, key, value)
        db.commit()
        db.refresh(db_role)
    return db_role

def get_skills(db: Session):
    return db.query(Skill).all()
