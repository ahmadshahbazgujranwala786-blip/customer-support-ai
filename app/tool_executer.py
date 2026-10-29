from app.tools.CRM.registry import CRM_TOOL_REGISTRY
from app.tools.FAQ.registry import FAQ_TOOL_REGISTRY
from app.tools.Commerce.registry import COMMERCE_TOOL_REGISTRY
from app.tools.research.registry import RESEARCH_TOOL_REGISTRY


ALL_TOOL_REGISTRY = {
    **CRM_TOOL_REGISTRY,
    **FAQ_TOOL_REGISTRY,
    **COMMERCE_TOOL_REGISTRY,
    **RESEARCH_TOOL_REGISTRY
}


def execute_tool(tool_name:str, arguments):

    tool = ALL_TOOL_REGISTRY.get(tool_name)

    if not tool:
        raise Exception(
            f"Tool not found: {tool_name}"
        )

    return tool.invoke(arguments)