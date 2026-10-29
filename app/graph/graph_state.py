from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class MultiAgentState(TypedDict):

    messages: Annotated[list, add_messages]

    user_id: int | None

    context: dict

    supervisor_plan: dict

    conversation_context: dict
    
    tasks: list

    agent_results: list

    final_response: str | None