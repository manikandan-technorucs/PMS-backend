from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Union, List

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.core.database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_bearer_scheme = HTTPBearer(auto_error=False)

# ── Canonical Role Names ─────────────────────────────────────
ROLE_ADMIN = "Admin"
ROLE_PROJECT_MANAGER = "Project Manager"
ROLE_TEAM_LEAD = "Team Lead"
ROLE_EMPLOYEE = "Employee"

# Full-access roles (Admin and Project Manager are equivalent)
FULL_ACCESS_ROLES = [ROLE_ADMIN, ROLE_PROJECT_MANAGER]
# Mid-level and above (can create/manage tasks, issues, timelogs, etc.)
TEAM_LEAD_PLUS_ROLES = [ROLE_ADMIN, ROLE_PROJECT_MANAGER, ROLE_TEAM_LEAD]
# All authenticated roles
ALL_ROLES = [ROLE_ADMIN, ROLE_PROJECT_MANAGER, ROLE_TEAM_LEAD, ROLE_EMPLOYEE]


# ── Password Utilities ──────────────────────────────────────
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# ── JWT ─────────────────────────────────────────────────────
def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


# ── Current User Dependency ─────────────────────────────────
def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
):
    """
    Decode the JWT, look up the User (with role eagerly loaded), and return
    the ORM object.  Raises 401 if token is missing/invalid.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id_str = payload.get("sub")
        if not user_id_str:
            print("[JWT DEBUG] No sub in payload")
            raise ValueError("No sub in payload")
        user_id = int(user_id_str)
    except (JWTError, ValueError, TypeError) as e:
        print(f"[JWT DEBUG] Decoding failed: {str(e)} | Secret Hash: {hash(settings.SECRET_KEY)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    from app.models.user import User
    user = (
        db.query(User)
        .options(joinedload(User.role))
        .filter(User.id == user_id)
        .first()
    )
    if not user or user.is_deleted:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


# ── Role Helper Utilities ────────────────────────────────────
def get_user_role_name(user) -> Optional[str]:
    """Returns the canonical role name of the user, or None."""
    return user.role.name if user and user.role else None


def is_full_access(user) -> bool:
    """Returns True if user is Admin or Project Manager (full access level)."""
    return get_user_role_name(user) in FULL_ACCESS_ROLES


def is_team_lead_plus(user) -> bool:
    """Returns True if user is Admin, Project Manager, or Team Lead."""
    return get_user_role_name(user) in TEAM_LEAD_PLUS_ROLES


def is_employee_only(user) -> bool:
    """Returns True if user is strictly an Employee (most restricted)."""
    return get_user_role_name(user) == ROLE_EMPLOYEE


# ── RBAC Guard ──────────────────────────────────────────────
class RoleChecker:
    """
    FastAPI dependency that validates the current user's role against
    an allow-list.  Usage:
        @router.post("/", dependencies=[Depends(allow_pm)])
    """
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user=Depends(get_current_user)):
        if current_user.role and current_user.role.name in self.allowed_roles:
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Requires one of: {', '.join(self.allowed_roles)}",
        )


# ── Pre-built RBAC Instances ─────────────────────────────────
# Full access — Admin and Project Manager are co-equal
allow_pm = RoleChecker(FULL_ACCESS_ROLES)

# Team Lead and above (Admin, Project Manager, Team Lead)
allow_team_lead_plus = RoleChecker(TEAM_LEAD_PLUS_ROLES)

# All roles (any authenticated user with a valid role)
allow_all_roles = RoleChecker(ALL_ROLES)

# Legacy aliases (kept for backward compatibility)
allow_admin = RoleChecker(FULL_ACCESS_ROLES)
allow_manager_plus = RoleChecker(FULL_ACCESS_ROLES)
allow_all = RoleChecker(ALL_ROLES)

def allow_authenticated(current_user=Depends(get_current_user)):
    return current_user


# ── Contextual Project RBAC Guard ────────────────────────────
class ProjectRoleChecker:
    """
    FastAPI dependency that validates if the user has a specific role IN THE CONTEXT of a project.
    Admin and Project Managers automatically bypass this constraint.
    """
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, project_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
        # Admin and Project Managers bypass project-level checks (full access)
        if current_user.role and current_user.role.name in FULL_ACCESS_ROLES:
            return current_user

        from app.models.project import project_users
        from sqlalchemy import select
        
        # Look up their assignment in the project
        assignment = db.execute(
            select(project_users.c.role_id).where(
                project_users.c.project_id == project_id,
                project_users.c.user_id == current_user.id
            )
        ).first()

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this project."
            )

        # If they lack a specific contextual role assigned (role_id is Null),
        # consider them a standard 'Member' and verify if 'Member' is allowed.
        if not assignment.role_id:
            if "Member" in self.allowed_roles:
                return current_user
        else:
            from app.models.roles import Role
            role = db.query(Role).filter(Role.id == assignment.role_id).first()
            if role and role.name in self.allowed_roles:
                return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Requires project-specific role: {', '.join(self.allowed_roles)}"
        )

allow_project_lead = ProjectRoleChecker(["Project Lead"])
allow_project_member = ProjectRoleChecker(["Project Lead", "Developer", "Member"])
