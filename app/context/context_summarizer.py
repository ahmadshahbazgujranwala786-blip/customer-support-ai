from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from app.llm.llm_factory import LLMFactory

def remove_duplicate_messages(context: dict) -> dict:
    """
    Remove duplicate messages from relevant memories
    if they already exist in the current conversation.
    """

    current_conversation = context["current_conversation"]
    relevant_memories = context["relevant_memories"]


    # Current conversation message IDs
    current_ids = {
        message["id"]
        for message in current_conversation
    }


    filtered_memories = []

    for memory in relevant_memories:

        if memory["id"] not in current_ids:
            filtered_memories.append(memory)


    context["relevant_memories"] = filtered_memories

    return context

# app/agents/context_summarizer_agent.py



# 1. Strict Schema for State Context Output
class SummarizedStateOutput(BaseModel):

    user_id: str = Field(description="Unique Customer/User ID")

    channel: str = Field(description="Communication channel (e.g., whatsapp, web)")

    customer_name: str = Field(description="Customer display name")

    summarized_history: str = Field(
        description="Concise LLM-friendly summary of past customer interactions and relevant memories"
    )
    current_intent: str = Field(
        description="Clear intent of what the customer wants from the current message"
    )

# 2. Class-Based Context Summarizer Agent
class ContextSummarizerAgent:
    
    def __init__(self):
        # Dedicated Low-Temperature LLM with Structured Output enforcement
        raw_llm = LLMFactory.get_summarizer_llm()
        self.llm = raw_llm.with_structured_output(SummarizedStateOutput)
        
        # System Prompt Setup
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
You are an expert Context Summarizer Agent for a Multi-Agent AI System.
Your task is to analyze raw customer data (Profile, History, Memories, and Current Message) and convert it into a strictly formatted State Payload for the Supervisor Agent.

RULES:
1. Extract and preserve the exact user_id, channel, and customer_name.
2. Summarize past history & long-term memories into a concise, high-signal text block (summarized_history).
3. Identify precisely what the customer is asking in the current message (current_intent).
4. Omit fluff, conversational noise, or irrelevant greetings.
"""),
        ("human", """
    Raw Input Data:
    - User ID: {user_id}
    - Channel: {channel}
    - Customer Name: {customer_name}
    - Raw Formatted Context:
    {formatted_context}
    """)
        ])
        
        # Chain setup using Runnable Pipe
        self.chain = self.prompt | self.llm

    def __call__(self, user_id: str, channel: str, customer_name: str, formatted_context: str) -> SummarizedStateOutput:
        return self.invoke(user_id, channel, customer_name, formatted_context)

    # 2. Explicit invoke support (e.g., agent.invoke(...))
    def invoke(self, user_id: str, channel: str, customer_name: str, formatted_context: str) -> SummarizedStateOutput:
        return self.chain.invoke({
            "user_id": user_id,
            "channel": channel,
            "customer_name": customer_name,
            "formatted_context": formatted_context
        })
