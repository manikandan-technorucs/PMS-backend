from app.core.database import SessionLocal
from app.services.team_service import add_team_member
from app.models.team import Team
from app.models.user import User

def simulate_assignment():
    db = SessionLocal()
    try:
        # Get first team and first user
        team = db.query(Team).first()
        user = db.query(User).first()
        
        if not team or not user:
            print("No team or user found to simulate assignment.")
            return
            
        print(f"Assigning user {user.email} to team {team.name}...")
        
        # Ensure user is not already in team
        if user in team.members:
            print("User already in team. Removing first for simulation...")
            team.members.remove(user)
            db.commit()
            
        success = add_team_member(db, team.id, user.id)
        print(f"Assignment success: {success}")
        
    finally:
        db.close()

if __name__ == "__main__":
    simulate_assignment()
