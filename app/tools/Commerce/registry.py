
from app.agents.Commerce.tools.get_order import get_order_details
from app.agents.Commerce.tools.product_tool import search_products
from app.agents.Commerce.tools.service_tool import search_services
from app.agents.Commerce.tools.cancel_order import cancel_order
from app.agents.Commerce.tools.create_order import create_order
from app.agents.Commerce.tools.update_order import update_order
COMMERCE_TOOL_REGISTRY = {
    "search_products": search_products,
    "search_services": search_services,
    "cancel_order": cancel_order,
    "get_order_details": get_order_details,
    "create_order": create_order,
    "update_order": update_order
}
