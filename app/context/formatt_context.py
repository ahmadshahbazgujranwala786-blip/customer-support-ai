def format_context(context: dict) -> str:

    lines = []

    lines.append("Customer:")
    lines.append(str(context["customer"]))

    lines.append("\nCurrent Message:")
    lines.append(context["current_message"]["content"])

    lines.append("\nConversation:")

    for msg in context["current_conversation"]:
        lines.append(f'{msg["role"]}: {msg["content"]}')

    lines.append("\nRelevant Memories:")

    for msg in context["relevant_memories"]:
        lines.append(f'{msg["role"]}: {msg["content"]}')

    return "\n".join(lines)