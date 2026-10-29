from langchain_core.tools import tool

from sqlalchemy import select

from app.database.session import SessionLocal
from app.models.order import Order


@tool
def cancel_order(
    order_id: int,
    reason: str = ""
) -> dict:
    """
    Cancel an existing order.
    Only pending orders can be cancelled.
    """

    session = SessionLocal()

    try:

        # 1. Find order
        print("Cancel order tool is being used........")
        order = session.scalar(
            select(Order).where(
                Order.id == order_id
            )
        )


        if order is None:

            return {
                "success": False,
                "message": "Order not found."
            }


        # 2. Check current status

        if order.status == "cancelled":

            return {
                "success": False,
                "message": "Order is already cancelled."
            }


        if order.status == "completed":

            return {
                "success": False,
                "message": "Completed orders cannot be cancelled."
            }


        # 3. Update order status

        order.status = "cancelled"


        # Optional:
        # Agar tumhare orders table me cancel_reason field hai
        # to yahan save kar sakte ho.


        session.commit()


        return {

            "success": True,

            "order_id": order.id,

            "status": order.status,

            "message": "Order cancelled successfully."
        }


    except Exception as e:

        session.rollback()

        return {

            "success": False,

            "message": str(e)
        }


    finally:

        session.close()