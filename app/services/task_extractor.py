from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from app.core.config import settings


class TaskSuggestion(BaseModel):
    """The schema the LLM MUST conform to. Pydantic validates it automatically."""
    title: str = Field(description="A short, clear, actionable task title (max 10 words)")
    description: str = Field(description="A detailed description of what needs to be done")
    priority: str = Field(description="Task priority: exactly one of LOW, MEDIUM, HIGH, URGENT")


_llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    google_api_key=settings.GEMINI_API_KEY,
)

# This wraps the LLM so its output is always a TaskSuggestion object
_structured_llm = _llm.with_structured_output(TaskSuggestion)

_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a project management assistant. "
        "Extract a well-defined task from the following chat transcript. "
        "The task should be actionable, specific, and clearly scoped.",
    ),
    ("human", "Chat transcript:\n{transcript}\n\nGenerate a task suggestion."),
])

# The pipe operator | builds a chain: prompt output → goes into _structured_llm
_chain = _prompt | _structured_llm


def extract_task_from_transcript(transcript: str) -> dict:
    """Called by the FastAPI router. Returns a plain dict for Node.js."""
    result: TaskSuggestion = _chain.invoke({"transcript": transcript})
    return {
        "title": result.title,
        "description": result.description,
        "priority": result.priority,
        "status": "TODO",
    }
