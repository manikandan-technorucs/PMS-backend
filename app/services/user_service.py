from sqlalchemy.orm import Session, joinedload
from app.models.user import User
from app.models.masters import Skill
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from app.utils.ids import generate_public_id

def get_user(db: Session, user_id: int):
    return db.query(User).options(
        joinedload(User.role),
        joinedload(User.department),
        joinedload(User.status),
        joinedload(User.location),
        joinedload(User.skills)
    ).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).options(
        joinedload(User.role),
        joinedload(User.department),
        joinedload(User.status),
        joinedload(User.location),
        joinedload(User.skills)
    ).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    public_id = generate_public_id("USR-")
    
    db_user = User(
        public_id=public_id,
        employee_id=user.employee_id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        role_id=user.role_id,
        dept_id=user.dept_id,
        status_id=user.status_id,
        location_id=user.location_id,
        manager_id=user.manager_id
    )
    
    if user.skill_ids:
        skills = db.query(Skill).filter(Skill.id.in_(user.skill_ids)).all()
        db_user.skills.extend(skills)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return get_user(db, db_user.id)

def update_user(db: Session, user_id: int, user_update: UserUpdate):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None
        
    update_data = user_update.model_dump(exclude_unset=True)
    
    if "skill_ids" in update_data:
        skill_ids = update_data.pop("skill_ids")
        if skill_ids is not None:
            skills = db.query(Skill).filter(Skill.id.in_(skill_ids)).all()
            db_user.skills = skills
            
    for key, value in update_data.items():
        setattr(db_user, key, value)
        
    db.commit()
    db.refresh(db_user)
    return get_user(db, db_user.id)

def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False
