from sqlalchemy.orm import Session, joinedload
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.utils.ids import generate_public_id
from app.services.automation_engine import execute_automation_event

def get_project(db: Session, project_id: int):
    return db.query(Project).options(
        joinedload(Project.manager),
        joinedload(Project.status),
        joinedload(Project.priority),
        joinedload(Project.department),
        joinedload(Project.team),
        joinedload(Project.users)
    ).filter(Project.id == project_id).first()

def get_projects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Project).options(
        joinedload(Project.manager),
        joinedload(Project.status),
        joinedload(Project.priority),
        joinedload(Project.department),
        joinedload(Project.team),
        joinedload(Project.users)
    ).offset(skip).limit(limit).all()

def create_project(db: Session, project: ProjectCreate):
    public_id = generate_public_id("PRJ-")
    db_project = Project(
        public_id=public_id,
        name=project.name,
        description=project.description,
        client=project.client,
        manager_id=project.manager_id,
        status_id=project.status_id,
        priority_id=project.priority_id,
        dept_id=project.dept_id,
        team_id=project.team_id,
        start_date=project.start_date,
        end_date=project.end_date,
        estimated_hours=project.estimated_hours
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    # Trigger Automations: PROJECT_CREATED
    if db_project.manager_id:
        manager = db.query(User).filter(User.id == db_project.manager_id).first()
        if manager and manager.email:
            payload = {
                "project_id": db_project.public_id,
                "project_name": db_project.name,
                "manager_name": f"{manager.first_name} {manager.last_name}"
            }
            execute_automation_event(
                db=db,
                event_name="PROJECT_CREATED",
                payload=payload,
                email_recipient=manager.email,
                entity_id=str(db_project.id)
            )

    return get_project(db, db_project.id)

def update_project(db: Session, project_id: int, project_update: ProjectUpdate):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        return None
    
    update_data = project_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_project, key, value)
        
    db.commit()
    db.refresh(db_project)
    return get_project(db, db_project.id)

def delete_project(db: Session, project_id: int):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project:
        db.delete(db_project)
        db.commit()
        return True
    return False

def add_user_to_project(db: Session, project_id: int, user_id: int):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if not db_project or not db_user:
        return False
        
    if db_user not in db_project.users:
        db_project.users.append(db_user)
        db.commit()
    return True

def remove_user_from_project(db: Session, project_id: int, user_id: int):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if not db_project or not db_user:
        return False
        
    if db_user in db_project.users:
        db_project.users.remove(db_user)
        db.commit()
    return True
