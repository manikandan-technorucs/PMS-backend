import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine, Base
from app.models import *

print("Dropping all existing tables in MySQL database...")
Base.metadata.drop_all(bind=engine)

print("Creating new updated tables...")
Base.metadata.create_all(bind=engine)

print("Database reset complete! You can now run `python app/seed.py` if you want mock data.")
