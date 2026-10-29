from langchain_core.messages import (
    SystemMessage,
    HumanMessage
)
from sympy import content

from app.llm.llm_factory import LLMFactory
from app.agents.response_generator.prompt import (
    RESPONSE_GENERATOR_PROMPT
)


response_llm = LLMFactory.get_response_generator_llm()



def response_generator(state):

    print("🚀 Response Generator Started")

    messages = state.get(
        "messages",
        []
    )

    conversation_context = state.get(
        "conversation_context",
        {}
    )
    customer_message = (
        messages[-1].content
        if messages
        else ""
    )


    context = state.get(
        "context",
        {}
    )

    agent_results = state.get(
        "agent_results",
        {}
    )

    generator_input = f"""

    Customer Message:

    {customer_message}


    Conversation Context:

    {conversation_context}


    Customer Context:

    {context}


     Agent Results:

    {state["agent_results"]}


    Generate the final response.

    """


    messages = [

        SystemMessage(
            content=RESPONSE_GENERATOR_PROMPT
        ),

        HumanMessage(
            content=generator_input
        )

    ]



    response = response_llm.invoke(
        messages
    )



    content = response.content


    if isinstance(content, list):

        final_response = "".join(
        item.get("text", "")
        if isinstance(item, dict)
        else str(item)
        for item in content
    )

    else:

      final_response = content



    print(
        "FINAL RESPONSE:",
        final_response
    )

    return {
        "final_response": final_response
    }