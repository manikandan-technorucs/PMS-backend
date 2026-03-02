from sqlalchemy.orm import Session, joinedload
from app.models.team import Team
from app.models.user import User
from app.schemas.team import TeamCreate, TeamUpdate
from app.utils.ids import generate_public_id

def get_team(db: Session, team_id: int):
    return db.query(Team).options(
        joinedload(Team.department)
    ).filter(Team.id == team_id).first()

def get_team_with_members(db: Session, team_id: int):
    return db.query(Team).options(
        joinedload(Team.department),
        joinedload(Team.members)
    ).filter(Team.id == team_id).first()

def get_teams(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Team).options(
        joinedload(Team.department)
    ).offset(skip).limit(limit).all()

def create_team(db: Session, team: TeamCreate):
    public_id = generate_public_id("TM-")
    
    db_team = Team(
        public_id=public_id,
        name=team.name,
        team_email=team.team_email,
        budget_allocation=team.budget_allocation,
        description=team.description,
        team_type=team.team_type,
        max_team_size=team.max_team_size,
        primary_communication_channel=team.primary_communication_channel,
        channel_id=team.channel_id,
        lead_id=team.lead_id,
        dept_id=team.dept_id,
        location_id=team.location_id
    )
    
    if team.member_ids:
        members = db.query(User).filter(User.id.in_(team.member_ids)).all()
        db_team.members = members
        
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return get_team(db, db_team.id)

def update_team(db: Session, team_id: int, team_update: TeamUpdate):
    db_team = db.query(Team).filter(Team.id == team_id).first()
    if not db_team:
        return None
        
    update_data = team_update.model_dump(exclude_unset=True)
    
    if "member_ids" in update_data:
        member_ids = update_data.pop("member_ids")
        if member_ids is not None:
            members = db.query(User).filter(User.id.in_(member_ids)).all()
            db_team.members = members
            
    for key, value in update_data.items():
        setattr(db_team, key, value)
        
    db.commit()
    db.refresh(db_team)
    return get_team(db, db_team.id)

def delete_team(db: Session, team_id: int):
    db_team = db.query(Team).filter(Team.id == team_id).first()
    if db_team:
        db.delete(db_team)
        db.commit()
        return True
    return False

def add_team_member(db: Session, team_id: int, user_id: int):
    db_team = db.query(Team).filter(Team.id == team_id).first()
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if db_team and db_user:
        if db_user not in db_team.members:
            db_team.members.append(db_user)
            db.commit()
            return True
    return False

def remove_team_member(db: Session, team_id: int, user_id: int):
    db_team = db.query(Team).filter(Team.id == team_id).first()
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if db_team and db_user:
        if db_user in db_team.members:
            db_team.members.remove(db_user)
            db.commit()
            return True
    return False
