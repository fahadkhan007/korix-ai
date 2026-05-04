from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from sqlalchemy.orm import Session
from app.models.db import ProjectMember, User


@tool
def get_project_members(project_id: str, config: RunnableConfig) -> str:
    """
    Fetches all members of a project with their name, user ID, and role.
    Use this when the user asks who is on the team or when you need a user ID.
    """
    db: Session = config["configurable"]["db"]
    results = (
        db.query(ProjectMember, User)
        .join(User, ProjectMember.userId == User.id)
        .filter(ProjectMember.projectId == project_id)
        .all()
    )
    if not results:
        return "No members found for this project."

    lines = [
        f"Name:{u.name} | ID:{u.id} | Role:{m.role}"
        for m, u in results
    ]
    return "\n".join(lines)


@tool
def find_user_by_name(name: str, project_id: str, config: RunnableConfig) -> str:
    """
    Finds a specific project member by partial name match.
    Returns the user ID and role.
    Use this when you need the user ID of a person before assigning a task.
    """
    db: Session = config["configurable"]["db"]
    result = (
        db.query(ProjectMember, User)
        .join(User, ProjectMember.userId == User.id)
        .filter(
            ProjectMember.projectId == project_id,
            User.name.ilike(f"%{name}%"),
        )
        .first()
    )
    if not result:
        return f"No member named '{name}' found in this project."
    m, u = result
    return f"Found — ID:{u.id} | Name:{u.name} | Role:{m.role}"
