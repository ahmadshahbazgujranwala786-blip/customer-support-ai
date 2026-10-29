from langchain_core.tools import tool

from sqlalchemy import select

from app.database.session import SessionLocal

from app.models.customer import Customer
from app.models.order import Order
from app.models.orderItems import OrderItem
from app.models.product import Product



@tool
def create_order(
    customer_id: int,
    products: list
) -> dict:
    """
    Create a new order.

    products format:

    [
        {
            "product_id": 1,
            "quantity": 2
        }
    ]
    """
    print("create order tool is being used.......")
    session = SessionLocal()

    try:

        # -------------------------
        # Check customer
        # -------------------------

        customer = session.scalar(
            select(Customer)
            .where(
                Customer.id == customer_id
            )
        )


        if customer is None:

            return {
                "success": False,
                "message": "Customer not found."
            }



        total_amount = 0

        order_items = []



        # -------------------------
        # Validate products
        # -------------------------

        for item in products:


            product = session.scalar(
                select(Product)
                .where(
                    Product.id == item["product_id"]
                )
            )


            if product is None:

                return {
                    "success": False,
                    "message":
                    f"Product {item['product_id']} not found."
                }



            quantity = item["quantity"]


            item_total = (
                product.price * quantity
            )


            total_amount += item_total



            order_items.append(
                {
                    "product": product,
                    "quantity": quantity,
                    "price": product.price
                }
            )



        # -------------------------
        # Create Order
        # -------------------------

        order = Order(

            customer_id=customer_id,

            total_amount=total_amount,

            status="pending"

        )


        session.add(order)

        session.flush()



        # -------------------------
        # Create Order Items
        # -------------------------

        for item in order_items:


            order_item = OrderItem(

                order_id=order.id,

                product_id=item["product"].id,

                quantity=item["quantity"],

                unit_price=item["price"]

            )


            session.add(order_item)



        session.commit()



        return {

            "success": True,

            "order_id": order.id,

            "total_amount": float(total_amount),

            "message":
            "Order created successfully."

        }



    except Exception as e:


        session.rollback()


        return {

            "success": False,

            "message": str(e)

        }


    finally:

        session.close()