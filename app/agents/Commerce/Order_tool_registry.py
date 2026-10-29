from app.agents.order.tools.product_tool import search_products
from app.agents.order.tools import (
    create_order,
    update_order,
    cancel_order,
    get_order_details
)


ORDER_TOOL_REGISTRY = {

    "search_products": search_products,

    "create_order": create_order,

    "update_order": update_order,

    "cancel_order": cancel_order,

    "get_order_details": get_order_details

}