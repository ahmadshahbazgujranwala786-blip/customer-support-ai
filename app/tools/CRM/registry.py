from app.agents.CRM.crm_tool import get_or_create_customer, update_customer

CRM_TOOL_REGISTRY = {
    "get_or_create_customer": get_or_create_customer,
    "update_customer": update_customer
}