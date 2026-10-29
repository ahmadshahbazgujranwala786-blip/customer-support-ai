import json
import logging

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool

from app.agents.supervisor.prompt import SUPERVISOR_AGENT_PROMPT
from app.llm.llm_factory import LLMFactory
from app.agents.FAQ.tools.faq_tools import get_knowledge
from app.agents.Commerce.tools.product_tool import search_products
from app.agents.Commerce.tools.create_order import create_order
from app.memory.memory_tools import save_message_memory

logger = logging.getLogger(__name__)


@tool
def search_business_knowledge(query: str, top_k: int = 3) -> dict:
    """Search approved company FAQs, policies, and business knowledge for an answer."""
    return get_knowledge(query=query, top_k=top_k)


class SupervisorAgent:
    """Single customer-facing agent for FAQ answers, order persistence, and customer memory."""

    def __init__(self):
        self.llm = LLMFactory.get_supervisor_llm().bind_tools([
            search_business_knowledge,
            search_products,
            create_order,
        ])
        self.tools = {
            "search_business_knowledge": search_business_knowledge,
            "search_products": search_products,
            "create_order": create_order,
        }

    def _messages(self, state: dict):
        messages = state.get("messages", [])
        user_message = messages[-1].content if messages else ""
        context = state.get("context") or {}
        customer = context.get("customer") or {}
        memories = context.get("relevant_memories") or []
        summarized = context.get("summarized_context") or ""

        system = (
            SUPERVISOR_AGENT_PROMPT
            + "\n\nCURRENT CUSTOMER ID: " + str(state.get("user_id"))
            + "\nCUSTOMER PROFILE: " + json.dumps(customer, default=str)
            + "\nRELEVANT CUSTOMER MEMORIES: " + json.dumps(memories, default=str)
            + "\nCONVERSATION SUMMARY: " + str(summarized)
        )
        return [
            SystemMessage(content=system),
            HumanMessage(content=user_message),
        ]

    def run(self, state: dict) -> dict:
        messages = self._messages(state)
        tool_trace = []

        # Tool use stays inside this one agent; no child-agent graph nodes are invoked.
        for _ in range(6):
            response = self.llm.invoke(messages)
            if not getattr(response, "tool_calls", None):
                answer = response.content
                if isinstance(answer, list):
                    answer = "".join(
                        item.get("text", "") if isinstance(item, dict) else str(item)
                        for item in answer
                    )
                answer = str(answer or "").strip()
                if not answer:
                    answer = "I'm sorry, I couldn't find a reliable answer to that. Could you rephrase your question?"
                self._save_customer_memory(state)
                return {
                    "final_response": answer,
                    "supervisor_plan": {
                        "mode": "single_agent",
                        "responsibilities": ["faq_response", "order_saving", "customer_memory_saving"],
                    },
                    "agent_results": {"supervisor": {"status": "completed", "tool_calls": tool_trace}},
                }

            messages.append(response)
            for call in response.tool_calls:
                name = call.get("name")
                args = call.get("args") or {}
                tool_fn = self.tools.get(name)
                if tool_fn is None:
                    result = {"success": False, "message": "Requested operation is unavailable."}
                else:
                    try:
                        result = tool_fn.invoke(args)
                    except Exception as exc:
                        logger.exception("Supervisor tool %s failed", name)
                        result = {"success": False, "message": str(exc)}
                tool_trace.append({"tool": name, "arguments": args, "result": result})
                messages.append(
                    ToolMessage(
                        content=json.dumps(result, default=str),
                        tool_call_id=call["id"],
                    )
                )

        self._save_customer_memory(state)
        return {
            "final_response": "I’m sorry, I couldn’t complete that request reliably. Please try again or clarify what you’d like me to do.",
            "supervisor_plan": {"mode": "single_agent"},
            "agent_results": {"supervisor": {"status": "tool_limit_reached", "tool_calls": tool_trace}},
        }

    @staticmethod
    def _save_customer_memory(state: dict) -> None:
        context = state.get("context") or {}
        message_id = context.get("current_message_id")
        customer_id = state.get("user_id")
        conversation_id = context.get("conversation_id")
        messages = state.get("messages") or []
        content = messages[-1].content if messages else ""
        if not all((message_id, customer_id, conversation_id, content)):
            return
        try:
            save_message_memory(
                message_id=int(message_id),
                customer_id=int(customer_id),
                conversation_id=int(conversation_id),
                content=str(content),
            )
        except Exception:
            # Memory failure must not prevent a customer from receiving a response.
            logger.exception("Could not save customer message to long-term memory")

    def __call__(self, state: dict) -> dict:
        return self.run(state)
