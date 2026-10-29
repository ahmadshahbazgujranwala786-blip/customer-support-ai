from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    ToolMessage
)

from app.tool_executer import execute_tool
from app.agents.task_manager import get_tasks
from app.llm.llm_factory import LLMFactory

from app.agents.CRM.prompt import CRM_SYSTEM_PROMPT

from app.agents.CRM.crm_tool import (
    get_or_create_customer,
    update_customer
)


# -----------------------------
# Model
# -----------------------------

crm_llm = LLMFactory.get_crm_llm()


# -----------------------------
# Bind Tools
# -----------------------------

crm_tools = [
    get_or_create_customer,
    update_customer
]


crm_llm = crm_llm.bind_tools(
    crm_tools
)


# -----------------------------
# Tool Registry
# -----------------------------

TOOLS = {

    "get_or_create_customer": get_or_create_customer,

    "update_customer": update_customer

}

# -----------------------------
# Agent
# -----------------------------

def crm_agent(state):

    print("🚀 CRM Agent Started")


    # ---------------------------------
    # 1. Get CRM Tasks
    # ---------------------------------

    crm_tasks = get_tasks(
        state,
        "CRM Agent"
    )


    if not crm_tasks:

        print(
            "No CRM task assigned"
        )

        return {

            "agent_results": {

                "crm": {

                    "status": "skipped",

                    "reason":
                    "No CRM task assigned"

                }

            }

        }



    # ---------------------------------
    # 2. Extract State Data
    # ---------------------------------

    user_id = state.get(
        "user_id"
    )


    context = state.get(
        "context",
        {}
    )


    messages = state.get(
        "messages",
        []
    )


    user_message = (

        messages[-1].content

        if messages

        else ""

    )



    # ---------------------------------
    # 3. Prepare Agent Input
    # ---------------------------------

    task_context = "\n".join(

        [

            f"""
Task ID:
{task.get('task_id')}

Objective:
{task.get('objective')}

Instructions:
{task.get('instructions')}

Expected Output:
{task.get('expected_output')}
"""
            for task in crm_tasks

        ]

    )


    agent_messages = [

        SystemMessage(
            content=
            CRM_SYSTEM_PROMPT
        ),


        HumanMessage(
            content=f"""

Customer ID:

{user_id}


Customer Context:

{context}


Customer Message:

{user_message}


Assigned CRM Tasks:

{task_context}


Execute these tasks using available tools.

Return structured customer information only.

"""
        )

    ]



    tool_results = []

    response = crm_llm.invoke(
            agent_messages
        )


    if not response.tool_calls:
        return None
    
    agent_messages.append(
            response
        )


    for tool_call in response.tool_calls:


        tool_name = tool_call["name"]

        tool_args = tool_call["args"]


        print(
                f"🔧 Executing Tool: {tool_name}"
            )


        result = execute_tool(
                tool_name,
                tool_args
            )


        tool_results.append({

                "tool": tool_name,

                "arguments": tool_args,

                "result": result

            })


        agent_messages.append(

                ToolMessage(

                    tool_call_id=
                    tool_call["id"],

                    content=
                    str(result)

                )

            )


    crm_result = {


        "status":
        "completed",


        "agent":
        "CRM Agent",


        "customer_id":
        user_id,


        "tasks_completed":

        [

            task["task_id"]

            for task in crm_tasks

        ],


        "tool_results":
        tool_results,


        "summary":

        response.content

    }



    print(
        "CRM RESULT:",
        crm_result
    )

    return {

        "agent_results": {

            "crm":
            crm_result

        }

    }