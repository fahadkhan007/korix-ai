from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import verify_token
from app.agent.runner import invoke_copilot
from app.services.task_extractor import extract_task_from_transcript

router = APIRouter(prefix="/api", tags=["AI"])


class ChatCopilotRequest(BaseModel):
    query: str
    projectId: str


class ConvertToTaskRequest(BaseModel):
    transcript: str
    projectId: str


@router.post("/chat-copilot")
async def chat_copilot(
    body: ChatCopilotRequest,
    _token: dict = Depends(verify_token),   # ← Zero-Trust guard
    db: Session = Depends(get_db),          # ← SQLAlchemy session
):
    """Called by Node.js when user sends @KorixAI message."""
    return invoke_copilot(body.query, body.projectId, db)


@router.post("/convert-to-task")
async def convert_to_task(
    body: ConvertToTaskRequest,
    _token: dict = Depends(verify_token),
):
    """Called by Node.js when user selects chat messages and clicks Convert to Task."""
    return extract_task_from_transcript(body.transcript)
