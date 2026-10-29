from langchain_core.messages import SystemMessage, HumanMessage

from app.llm.llm_factory import LLMFactory
from app.agents.FAQ.tools.faq_tools import get_knowledge
from app.agents.task_manager import get_tasks


llm = LLMFactory.get_faq_llm()


SYSTEM_PROMPT = """
You are a professional Business FAQ Agent.

Your responsibility is to retrieve and structure business knowledge.

You do NOT generate the final customer response.

Your job:

- Analyze the assigned FAQ task.
- Use retrieved business knowledge only.
- Never invent information.
- Return structured factual information for the Response Generator Agent.
- If information is unavailable, clearly mention that.

Your output will be stored in:

state["agent_results"]["faq"]
"""


def faq_agent(state):

    print("========== FAQ AGENT ==========")


    # ---------------------------------
    # 1. Get Assigned Tasks
    # ---------------------------------

    faq_tasks = get_tasks(
        state,
        "FAQ Agent"
    )


    if not faq_tasks:

        print(
            "No FAQ task assigned"
        )

        return {
            "agent_results": {
                "faq": {
                    "status": "skipped",
                    "reason": "No FAQ task assigned"
                }
            }
        }



    # ---------------------------------
    # 2. Extract Customer Context
    # ---------------------------------

    user_id = state.get(
        "user_id"
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
    # 3. Prepare Task Context
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
            for task in faq_tasks
        ]
    )


    # ---------------------------------
    # 4. Retrieve Knowledge
    # ---------------------------------

    search_result = get_knowledge(
        user_message
    )


    knowledge = search_result.get(
        "knowledge",
        []
    )


    if knowledge:

        knowledge_context = "\n\n".join(
            [
                f"""
Title: {item['title']}

Category:
{item['category']}

Content:
{item['content']}
"""
                for item in knowledge
            ]
        )

    else:

        knowledge_context = (
            "No relevant business knowledge found."
        )



    # ---------------------------------
    # 5. LLM Processing
    # ---------------------------------

    llm_messages = [

        SystemMessage(
            content=SYSTEM_PROMPT
        ),

        HumanMessage(
            content=f"""

Customer Message:

{user_message}


Customer ID:

{user_id}


Assigned Tasks:

{task_context}


Retrieved Knowledge:

{knowledge_context}


Create structured FAQ results.
"""
        )

    ]


    response = llm.invoke(
        llm_messages
    )



    # ---------------------------------
    # 6. Store Agent Result
    # ---------------------------------

    faq_result = {

        "status": "completed",

        "agent": "FAQ Agent",

        "customer_id": user_id,

        "tasks_completed": [

            task["task_id"]

            for task in faq_tasks

        ],

        "knowledge_used": knowledge,

        "summary": response.content

    }



    print(
        "FAQ RESULT:",
        faq_result
    )



    # ---------------------------------
    # 7. Update Graph State
    # ---------------------------------

    return {

        "agent_results": {

            "faq": faq_result

        }

    }