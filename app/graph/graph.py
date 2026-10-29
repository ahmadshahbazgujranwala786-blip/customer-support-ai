from langgraph.graph import StateGraph, START, END

from app.agents.supervisor.agent import SupervisorAgent
from app.graph.graph_state import MultiAgentState

workflow = StateGraph(MultiAgentState)
workflow.add_node("supervisor", SupervisorAgent())
workflow.add_edge(START, "supervisor")
workflow.add_edge("supervisor", END)

graph = workflow.compile()
