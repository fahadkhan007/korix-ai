from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig 
from sqlalchemy.orm import Session
from app.models.db import Task


@tool
def get_project_tasks(project_id: str, config: RunnableConfig) -> str:
    """
    Fetches ALL tasks for a project.
    Returns title, status, priority, and assignee for each task.
    Use this when the user asks about task status, workload, or project progress.
    """
    db: Session = config["configurable"]["db"]  # ← Extract db here, not in signature
    tasks = db.query(Task).filter(Task.projectId == project_id).all()
    if not tasks:
        return "No tasks found for this project."

    lines = []
    for t in tasks:
        assignee = t.assigneeId or "Unassigned"
        due = str(t.dueDate.date()) if t.dueDate else "No due date"
        lines.append(
            f"ID:{t.id} | {t.title} | Status:{t.status} | "
            f"Priority:{t.priority} | AssigneeId:{assignee} | Due:{due}"
        )
    return "\n".join(lines)


@tool
def find_task_by_name(name: str, project_id: str, config: RunnableConfig) -> str:
    """
    Finds a specific task by partial title match within a project.
    Returns the task ID, full title, and current status.
    Use this when you need the ID of a task before taking an action on it.
    """
    db: Session = config["configurable"]["db"]
    task = (
        db.query(Task)
        .filter(Task.projectId == project_id, Task.title.ilike(f"%{name}%"))
        .first()
    )
    if not task:
        return f"No task matching '{name}' found in this project."
    return (
        f"Found — ID:{task.id} | Title:{task.title} | "
        f"Status:{task.status} | Priority:{task.priority}"
    )
