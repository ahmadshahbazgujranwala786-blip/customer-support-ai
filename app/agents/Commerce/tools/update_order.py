from langchain_core.tools import tool

from sqlalchemy import select

from app.database.session import SessionLocal
from app.models.order import Order

@tool
def update_order(
    order_id: int,
    updates: dict
) -> dict:
    """
    Update allowed fields of an existing order.
    """
    print("update order tool is being used........")
    session = SessionLocal()

    try:

        # 1. Find order

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


        # 2. Status validation

        if order.status == "cancelled":

            return {
                "success": False,
                "message": "Cancelled order cannot be updated."
            }


        # 3. Allowed fields

        allowed_fields = {
            "shipping_address",
            "payment_method",
            "notes",
            "status"
        }


        updated_fields = []

        VALID_STATUSES = {
        "pending",
        "completed",
        "cancelled"
        }
        # 4. Apply updates

        for field, value in updates.items():

            if field not in allowed_fields:

                continue
            if field == "status":
                if field not in VALID_STATUSES:
                     return {
                "success": False,
                "message": (
                    f"Invalid status '{value}'. "
                    f"Allowed values are: {VALID_STATUSES}"
                )
            }

            setattr(
                order,
                field,
                value
            )

            updated_fields.append(field)


        if not updated_fields:

            return {
                "success": False,
                "message": "No valid fields provided."
            }

        # 5. Commit changes

        session.commit()

        return {

            "success": True,

            "order_id": order.id,

            "updated_fields": updated_fields,

            "message": "Order updated successfully."
        }


    except Exception as e:

        session.rollback()

        return {

            "success": False,

            "message": str(e)
        }


    finally:

        session.close()