from sqlalchemy.orm import Session, joinedload
from app.models.milestone import Milestone
from app.schemas.milestone import MilestoneCreate, MilestoneUpdate
from app.utils.ids import generate_public_id

def get_milestone(db: Session, milestone_id: int):
    return db.query(Milestone).options(
        joinedload(Milestone.project),
        joinedload(Milestone.status)
    ).filter(Milestone.id == milestone_id).first()

def get_milestones(db: Session, project_id: int = None, skip: int = 0, limit: int = 100):
    query = db.query(Milestone).options(
        joinedload(Milestone.project),
        joinedload(Milestone.status)
    )
    if project_id:
        query = query.filter(Milestone.project_id == project_id)
    return query.offset(skip).limit(limit).all()

def create_milestone(db: Session, milestone: MilestoneCreate):
    public_id = generate_public_id("MLS-")
    db_milestone = Milestone(
        public_id=public_id,
        title=milestone.title,
        description=milestone.description,
        start_date=milestone.start_date,
        end_date=milestone.end_date,
        project_id=milestone.project_id,
        status_id=milestone.status_id
    )
    db.add(db_milestone)
    db.commit()
    db.refresh(db_milestone)
    return get_milestone(db, db_milestone.id)

def update_milestone(db: Session, milestone_id: int, milestone_update: MilestoneUpdate):
    db_milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not db_milestone:
        return None
    
    update_data = milestone_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_milestone, key, value)
        
    db.commit()
    db.refresh(db_milestone)
    return get_milestone(db, db_milestone.id)

def delete_milestone(db: Session, milestone_id: int):
    db_milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if db_milestone:
        db.delete(db_milestone)
        db.commit()
        return True
    return False
