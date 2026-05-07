import json
import re
from langchain_core.messages import HumanMessage
from sqlalchemy.orm import Session

from app.agent.graph import graph


def _parse_agent_response(content: str) -> dict:
    """
    Looks for a special ACTION_JSON block in the agent's text response.
    If found: returns {"type": "action", "action": "...", "payload": {...}, "message": "..."}
    If not:   returns {"type": "message", "message": "..."}
    """
    match = re.search(r"ACTION_JSON:\s*(\{.*?\})", content, re.DOTALL)
    if match:
        try:
            action_data = json.loads(match.group(1))
            # Everything before ACTION_JSON: is the human-readable message
            clean_message = content[: match.start()].strip()
            return {
                "type": "action",
                "action": action_data.get("action"),
                "payload": {k: v for k, v in action_data.items() if k != "action"},
                "message": clean_message,
            }
        except json.JSONDecodeError:
            pass  # Malformed JSON — fall through to plain message

    return {"type": "message", "message": content}


def invoke_copilot(query: str, project_id: str, db: Session) -> dict:
    """
    The single public function called by the FastAPI router.
    Runs the LangGraph agent and returns a structured dict for Node.js.
    """
    try:
        result = graph.invoke(
            {
                "messages": [HumanMessage(content=query)],
                "project_id": project_id,
            },
            config={"configurable": {"db": db}},
        )
        final_content = result["messages"][-1].content
        return _parse_agent_response(final_content)

    except Exception as e:
        print(f"[runner] Agent error: {e}")
        return {
            "type": "message",
            "message": "Sorry, I ran into an error. Please try again.",
        }
