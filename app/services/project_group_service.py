from sqlalchemy.orm import Session
from app.models.project_group import ProjectGroup
from app.schemas.project_group import ProjectGroupCreate, ProjectGroupUpdate

def get_project_group(db: Session, group_id: int):
    return db.query(ProjectGroup).filter(ProjectGroup.id == group_id).first()

def get_project_groups(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ProjectGroup).offset(skip).limit(limit).all()

def create_project_group(db: Session, group: ProjectGroupCreate):
    db_group = ProjectGroup(
        name=group.name,
        description=group.description
    )
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

def update_project_group(db: Session, group_id: int, group_update: ProjectGroupUpdate):
    db_group = get_project_group(db, group_id)
    if not db_group:
        return None
    
    update_data = group_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_group, key, value)
    
    db.commit()
    db.refresh(db_group)
    return db_group

def delete_project_group(db: Session, group_id: int):
    db_group = get_project_group(db, group_id)
    if not db_group:
        return False
    db.delete(db_group)
    db.commit()
    return True
