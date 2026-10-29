from langchain_core.tools import tool
from app.models.orderItems import OrderItem
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database.session import SessionLocal
from app.models.order import Order


@tool
def get_order_details(order_id: int) -> dict:
    """
    Get complete details of an order including products.
    """
    print("Get order agent is being used.......")
    session = SessionLocal()

    try:

        order = session.scalar(
        select(Order)
        .options(
        selectinload(Order.items)
        .selectinload(OrderItem.product)
        )
        .where(
         Order.id == order_id
        )
)

        if order is None:
            
            return {
                "success": False,
                "message": "Order not found."
            }


        items = []

        for item in order.items:

            items.append(
                {
                    "product_id": item.product.id,
                    "product_name": item.product.name,
                    "quantity": item.quantity,
                    "unit_price": float(item.unit_price)
                }
            )


        return {

            "success": True,

            "order": {

                "id": order.id,

                "status": order.status,

                "total_amount": float(
                    order.total_amount
                ),

                "shipping_address": order.shipping_address,

                "payment_method": order.payment_method,

                "payment_status": order.payment_status,

                "items": items
            }
        }


    except Exception as e:

        return {

            "success": False,

            "message": str(e)
        }


    finally:

        session.close()