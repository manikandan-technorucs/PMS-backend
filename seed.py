from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.masters import Department, UserStatus, Skill, Status, Priority
from app.models.roles import Role
from app.models import *  

def seed_data(db: Session):
    Base.metadata.create_all(bind=engine)
    
    if db.query(Department).count() == 0:
        departments = [
            Department(name="Engineering"),
            Department(name="Sales"),
            Department(name="HR"),
            Department(name="O365"),
            Department(name="Bussiness Analyst"),
        ]
        db.add_all(departments)

    if db.query(UserStatus).count() == 0:
        statuses = [
            UserStatus(name="Active"),
            UserStatus(name="Inactive"),
            UserStatus(name="Onboarding"),
        ]
        db.add_all(statuses)

    if db.query(Status).count() == 0:
        core_statuses = [
            Status(name="Planning"),
            Status(name="Active"),
            Status(name="In Progress"),
            Status(name="Completed"),
            Status(name="Pending"),
        ]
        db.add_all(core_statuses)

    if db.query(Priority).count() == 0:
        priorities = [
            Priority(name="Low"),
            Priority(name="Medium"),
            Priority(name="High"),
            Priority(name="Critical"),
        ]
        db.add_all(priorities)

    all_perms_except_user_mutations = {
        "proj-view": True, "proj-create": True, "proj-edit": True, "proj-delete": True,
        "task-view": True, "task-create": True, "task-edit": True, "task-delete": True,
        "user-view": True, "user-create": False, "user-edit": False, "user-delete": False,
        "report-view": True, "report-export": True,
        "settings-view": True, "settings-edit": True
    }

    team_lead_perms = {
        "user-view": True,
        "task-view": True, "task-create": True, "task-edit": True, "task-delete": True
    }

    if db.query(Role).count() == 0:
        roles = [
            Role(name="Super Admin", permissions=all_perms_except_user_mutations),
            Role(name="Manager", permissions=all_perms_except_user_mutations),
            Role(name="Business Analyst", permissions=all_perms_except_user_mutations),
            Role(name="Team Lead", permissions=team_lead_perms),
            Role(name="Employee", permissions={}),
        ]
        db.add_all(roles)

    if db.query(Skill).count() == 0:
        skills = [
            Skill(name="React"),
            Skill(name="Python"),
            Skill(name="FastAPI"),
            Skill(name="UI/UX Design"),
            Skill(name="Node.js"),
            Skill(name=".NET"),
            Skill(name="DevOps"),
            Skill(name="Project Management"),
            Skill(name="Data Analytics"),
        ]
        db.add_all(skills)

    if db.query(User).count() == 0:
        admin_role = db.query(Role).filter(Role.name == "Super Admin").first()
        admin_user = User(
            public_id="USR-ADMIN-001",
            employee_id="ADM001",
            first_name="Admin",
            last_name="User",
            email="admin@technorucs.com",
            username="admin",
            role_id=admin_role.id if admin_role else None
        )
        db.add(admin_user)

    # Seed Email Templates if they don't exist
    def ensure_template(name, subject, body_html, body_text):
        existing = db.query(EmailTemplate).filter(EmailTemplate.name == name).first()
        if not existing:
            db.add(EmailTemplate(
                name=name,
                subject=subject,
                body_html=body_html,
                body_text=body_text,
                is_active=True
            ))
            db.commit()

    ensure_template(
        "New Task Assigned",
        "New Task: {{ task_title }}",
        "<p>Hi {{ assignee_name }},</p><p>A new task <strong>{{ task_title }}</strong> has been assigned to you in project <strong>{{ project_name }}</strong>.</p>",
        "Hi {{ assignee_name }},\n\nA new task {{ task_title }} has been assigned to you in project {{ project_name }}."
    )
    ensure_template(
        "Project Created",
        "New Project: {{ project_name }}",
        "<p>Hi {{ manager_name }},</p><p>A new project <strong>{{ project_name }}</strong> has been created and you are the manager.</p>",
        "Hi {{ manager_name }},\n\nA new project {{ project_name }} has been created and you are the manager."
    )
    ensure_template(
        "Timesheet Status Updated",
        "Timesheet {{ new_status }}: {{ timesheet_name }}",
        "<p>Hi {{ user_name }},</p><p>Your timesheet <strong>{{ timesheet_name }}</strong> has been <strong>{{ new_status }}</strong>.</p>",
        "Hi {{ user_name }},\n\nYour timesheet {{ timesheet_name }} has been {{ new_status }}."
    )
    ensure_template(
        "Team Joined",
        "Welcome to {{ team_name }}",
        "<p>Hi {{ user_name }},</p><p>You have been added to the team <strong>{{ team_name }}</strong> ({{ team_id }}).</p>",
        "Hi {{ user_name }},\n\nYou have been added to the team {{ team_name }} ({{ team_id }})."
    )

    # Seed Automation Rules if they don't exist for specific events
    def ensure_rule(event_name, template_name):
        existing = db.query(AutomationRule).filter(AutomationRule.trigger_event == event_name).first()
        if not existing:
            template = db.query(EmailTemplate).filter(EmailTemplate.name == template_name).first()
            if template:
                db.add(AutomationRule(trigger_event=event_name, template_id=template.id, is_active=True))
                db.commit()

    ensure_rule("TASK_ASSIGNED", "New Task Assigned")
    ensure_rule("PROJECT_CREATED", "Project Created")
    ensure_rule("TEAM_ASSIGNED", "Team Joined")
    ensure_rule("TIMESHEET_APPROVED", "Timesheet Status Updated")

    print("Database seeding completed.")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()
