from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage

from app.agent.state import AgentState
from app.agent.prompts import SYSTEM_PROMPT
from app.agent.tools.task import get_project_tasks, find_task_by_name
from app.agent.tools.member import get_project_members, find_user_by_name
from app.agent.tools.chat import get_recent_chat_messages
from app.core.config import settings


ALL_TOOLS = [
    get_project_tasks,
    find_task_by_name,
    get_project_members,
    find_user_by_name,
    get_recent_chat_messages,
]

# Gemini 1.5 Flash — free tier, great at tool use
# We pass the API key explicitly from pydantic settings
# because pydantic-settings reads .env into its object, not into os.environ
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    google_api_key=settings.GEMINI_API_KEY,
)

# bind_tools() tells the LLM: "You have access to these functions"
# The LLM won't call them directly — it just knows they exist and can request them
llm_with_tools = llm.bind_tools(ALL_TOOLS)


def chat_node(state: AgentState) -> dict:
    """
    The main thinking node.
    Injects the system prompt, then calls the LLM.
    Returns {"messages": [ai_response]} which LangGraph appends to state.
    """
    messages = state["messages"]
    project_id = state["project_id"]

    if not isinstance(messages[0], SystemMessage):
        sys_msg = SystemMessage(content=SYSTEM_PROMPT.format(project_id=project_id))
        messages = [sys_msg, *messages]

    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    """
    The conditional edge function.
    Returns the name of the next node to go to.
    LangGraph calls this after every chatbot node execution.
    """
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"   # Go run the tools
    return END           # We're done, exit the graph


# ── Build the Graph ────────────────────────────────────────
builder = StateGraph(AgentState)

builder.add_node("chatbot", chat_node)
builder.add_node("tools", ToolNode(ALL_TOOLS))

builder.add_edge(START, "chatbot")                          # Always start at chatbot
builder.add_conditional_edges("chatbot", should_continue)  # Then decide: tools or END
builder.add_edge("tools", "chatbot")                       # After tools, always think again

graph = builder.compile()
