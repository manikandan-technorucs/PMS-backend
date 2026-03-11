from app.core.database import SessionLocal
from app.models.user import User

db = SessionLocal()
try:
    users = db.query(User).all()
    print(f"Success! Users loaded: {len(users)}")
except Exception as e:
    print(f"Error querying users: {e}")
finally:
    db.close()
