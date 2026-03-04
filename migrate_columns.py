"""One-time migration script to add missing columns to existing tables."""
from app.core.database import engine
from sqlalchemy import text, inspect

def migrate():
    insp = inspect(engine)
    
    # --- timelogs table ---
    existing = [c["name"] for c in insp.get_columns("timelogs")]
    conn = engine.connect()
    
    if "log_title" not in existing:
        conn.execute(text("ALTER TABLE timelogs ADD COLUMN log_title VARCHAR(255)"))
        print("  + timelogs.log_title")
    if "billing_type" not in existing:
        conn.execute(text("ALTER TABLE timelogs ADD COLUMN billing_type VARCHAR(50) DEFAULT 'Billable'"))
        print("  + timelogs.billing_type")
    if "approval_status" not in existing:
        conn.execute(text("ALTER TABLE timelogs ADD COLUMN approval_status VARCHAR(50) DEFAULT 'Pending'"))
        print("  + timelogs.approval_status")
    if "timesheet_id" not in existing:
        conn.execute(text("ALTER TABLE timelogs ADD COLUMN timesheet_id INTEGER REFERENCES timesheets(id)"))
        print("  + timelogs.timesheet_id")
    
    # --- milestones table (owner_id already added, but confirm) ---
    ms_existing = [c["name"] for c in insp.get_columns("milestones")]
    if "owner_id" not in ms_existing:
        conn.execute(text("ALTER TABLE milestones ADD COLUMN owner_id INTEGER REFERENCES users(id)"))
        print("  + milestones.owner_id")
    
    conn.commit()
    conn.close()
    
    # Verify
    insp2 = inspect(engine)
    print("\ntimelogs columns:", [c["name"] for c in insp2.get_columns("timelogs")])
    print("milestones columns:", [c["name"] for c in insp2.get_columns("milestones")])
    print("\nMigration complete!")

if __name__ == "__main__":
    migrate()
