from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage

from app.graph.graph import graph
from app.context.context_builder import build_context
from app.tools.database_tools.customer_tools import get_customer_by_user_id, create_customer
from app.memory.retrieval_tools import retrieve_memory
from app.tools.database_tools.conversation_tools import get_or_create_conversation
from app.context.context_summarizer import remove_duplicate_messages, ContextSummarizerAgent
from app.tools.database_tools.message_tools import save_message, get_conversation_messages
from app.context.formatt_context import format_context


class ConversationService:
    print("ConversationService initialized successfully.")

    def __init__(self, db: Session):
        self.db = db
        self.summarizer_agent = ContextSummarizerAgent()

    def prepare_context(self, user_id: str, channel: str, sender_name: str, message: str):
        customer = get_customer_by_user_id(
            db=self.db, user_id=user_id, channel=channel
        )
        if customer is None:
            customer = create_customer(
                db=self.db, user_id=user_id, channel=channel, sender_name=sender_name
            )

        conversation = get_or_create_conversation(
            db=self.db, customer_id=customer.id, channel=channel
        )
        saved_message = save_message(
            db=self.db,
            conversation_id=conversation.id,
            sender_type="user",
            message_type="text",
            content=message,
        )

        memories = retrieve_memory(
            db=self.db, customer_id=customer.id, query=message, limit=5
        )
        messages = get_conversation_messages(
            db=self.db, conversation_id=conversation.id
        )
        context = build_context(
            customer=customer,
            current_message=saved_message,
            current_conversation=messages,
            relevant_memories=memories,
        )
        context = remove_duplicate_messages(context)
        formatted_context = format_context(context)
        summarized_output = self.summarizer_agent(
            user_id=customer.user_id,
            channel=channel,
            customer_name=customer.sender_name or sender_name,
            formatted_context=formatted_context,
        )

        summary_text = summarized_output.summarized_history
        conversation_context = {
            "is_first_message": len(messages) <= 1,
            "message_count": len(messages),
            "recent_messages": [
                {"role": msg.sender_type, "content": msg.content}
                for msg in messages[-5:]
            ],
        }
        return {
            "customer": customer,
            "conversation_id": conversation.id,
            "current_message": saved_message,
            "summarized_context": summary_text,
            "conversation_context": conversation_context,
            "relevant_memories": context.get("relevant_memories", []),
        }

    def process_user_message(
        self,
        user_id: str,
        channel: str,
        sender_name: str,
        message: str,
    ) -> str:
        context_data = self.prepare_context(
            user_id=user_id,
            channel=channel,
            sender_name=sender_name,
            message=message,
        )
        customer = context_data["customer"]
        conversation_id = context_data["conversation_id"]
        saved_message = context_data["current_message"]
        summarized_context = context_data["summarized_context"]
        conversation_context = context_data["conversation_context"]

        initial_state = {
            "messages": [HumanMessage(content=message)],
            "user_id": customer.id,
            "context": {
                "customer": {
                    "id": customer.id,
                    "user_id": customer.user_id,
                    "name": customer.sender_name,
                    "channel": channel,
                },
                "conversation_context": conversation_context,
                "channel": channel,
                "summarized_context": summarized_context,
                "relevant_memories": context_data.get("relevant_memories", []),
                "current_message_id": saved_message.id,
                "conversation_id": conversation_id,
            },
            "conversation_context": conversation_context,
            "supervisor_plan": {},
            "tasks": [],
            "agent_results": {},
            "final_response": None,
        }

        print("Invoking single Supervisor Agent workflow...")
        final_state = graph.invoke(initial_state)
        response = final_state.get("final_response")
        if response is None or not str(response).strip():
            response = "I'm sorry, I couldn't generate a response to that message."
        response = str(response).strip()

        save_message(
            db=self.db,
            conversation_id=conversation_id,
            sender_type="bot",
            message_type="text",
            content=response,
        )
        return response
