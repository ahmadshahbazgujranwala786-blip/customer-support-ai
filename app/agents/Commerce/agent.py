import json

from app.llm.llm_factory import LLMFactory
from app.agents.Commerce.tools import (
    create_order,
    update_order,
    cancel_order,
    get_order_details
)
from app.agents.Commerce.tools.product_tool import search_products
from app.tool_executer import execute_tool
from app.agents.task_manager import get_tasks
from app.agents.Commerce.tools.service_tool import search_services

commerce_llm = LLMFactory.get_commerce_llm()


order_tools = [

    create_order,
    get_order_details,
    update_order,
    cancel_order,
    search_products,
    search_services

]


commerce_llm = commerce_llm.bind_tools(order_tools)



# -----------------------------
# System Prompt
# -----------------------------

ORDER_AGENT_PROMPT = """

You are an Order Management Agent.

Your job is to execute assigned order-related tasks.

You can handle:

- Product search
- Product information retrieval
- Order creation
- Order updates
- Order cancellation
- Order status checking
- Service search
You can search both physical products and company services.

Use:
- search_products for hardware/products
- search_services for software solutions, automation, subscriptions, consulting etc.

RULES:

- Always use tools for database operations.
- Never invent products or order information.
- Never create fake order IDs.
- Always verify information before modifying orders.
- Never directly answer the customer.
- Return structured results for the Response Generator Agent.

Your output will be stored in:

state["agent_results"]["order"]

"""



def commerce_agent(state):

    print("========== COMMERCE AGENT ==========")

    order_tasks = get_tasks(
        state,
        "Commerce Agent"
    )

    if not order_tasks:

        return {}


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


    last_message = (
        messages[-1].content
        if messages
        else ""
    )


    agent_input = f"""

Customer ID:
{user_id}


Customer Context:
{json.dumps(context, indent=2)}


Customer Message:
{last_message}


Assigned Tasks:

{json.dumps(order_tasks, indent=2)}


Complete only these assigned tasks.

Return structured results.
"""



    llm_messages = [

        {
            "role": "system",
            "content": ORDER_AGENT_PROMPT
        },

        {
            "role": "user",
            "content": agent_input
        }

    ]



    tool_outputs = []


    response = commerce_llm.invoke(
            llm_messages
        )


    if not response.tool_calls:
        return None


    for tool_call in response.tool_calls:

            tool_name = tool_call["name"]

            args = tool_call["args"]



            print(
                "Executing:",
                tool_name,
                args
            )


            result = execute_tool(
                tool_name,
                args
            )


            tool_outputs.append({

                "tool": tool_name,

                "arguments": args,

                "result": result

            })


            llm_messages.append({

                "role": "tool",

                "content": str(result),

                "tool_call_id":
                    tool_call["id"]

            })



    agent_result = {

        "status": "completed",

        "agent": "Commerce Agent",

        "customer_id": user_id,


        "tasks_completed": [

            task["task_id"]

            for task in order_tasks

        ],


        "tool_results": tool_outputs,


        "summary":

            response.content

    }



    print(
        "ORDER RESULT:",
        agent_result
    )




    return {


        "agent_results": {


            "order": agent_result


        }

    }