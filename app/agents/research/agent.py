from app.agents.research.tools.search_tool import search_tool

from app.llm.llm_factory import LLMFactory

researcher_llm = LLMFactory.get_research_llm()



# Bind once
researcher_llm = researcher_llm.bind_tools(
    [search_tool]
)


RESEARCHER_AGENT_PROMPT = """
You are a Researcher Agent.

Your job is to collect external information.

Rules:

- Use the Tavily search tool whenever external information is required.
- Never invent facts.
- Always rely on the search results.
- Perform at most ONE tool call.
"""

def researcher_agent(state):

    print("========== RESEARCHER AGENT ==========")

    messages = [
        {
            "role": "system",
            "content": RESEARCHER_AGENT_PROMPT
        }
    ] + state["messages"]

    response = researcher_llm.invoke(messages)

    tool_name = None
    tool_args = None
    tool_result = None

    if response.tool_calls:

        tool_call = response.tool_calls[0]

        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        print(f"\n🔧 Executing Tool")
        print(f"Tool: {tool_name}")
        print(f"Arguments: {tool_args}")

        # Execute Tavily directly
        tool_result = search_tool.invoke(tool_args)

        print("\n✅ Tool Result:")
        print(tool_result)

    else:

        print("No tool call generated.")

    return {
        "agent_results": {
            "researcher": {
                "status": "completed",
                "customer_id": state["user_id"],
                "tasks_completed": [
                    task["task_id"]
                    for task in state["tasks"]
                    if task["agent"] == "Researcher Agent"
                ],
                "tool_results": [
                    {
                        "tool": tool_name,
                        "arguments": tool_args,
                        "result": tool_result
                    }
                ] if tool_name else [],
                "summary": tool_result
            }
        }
    }