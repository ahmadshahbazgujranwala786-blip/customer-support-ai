from psycopg2.extras import RealDictCursor
import psycopg2
from langchain_core.tools import tool

DATABASE_CONFIG = {
    "dbname": "customer_support",
    "user": "postgres",
    "password": "123456",
    "host": "localhost",
}

@tool
def get_or_create_customer(
    channel: str,
    user_id: str,
    sender_name: str,
) -> dict:
    """
    Use this tool to create new Customers in the Customer Table
    """
    try:

        conn = psycopg2.connect(**DATABASE_CONFIG)

        cur = conn.cursor(cursor_factory=RealDictCursor)

        # ----------------------------
        # Search Existing Customer
        # ----------------------------

        cur.execute(
            """
            SELECT *
            FROM customers
            WHERE channel=%s
            AND user_id=%s
            LIMIT 1
            """,
            (
                channel,
                user_id,
            ),
        )

        customer = cur.fetchone()

        if customer:

            cur.close()
            conn.close()

            return {

                "success": True,

                "customer": customer,

                "created": False,
            }

        # ----------------------------
        # Create Customer
        # ----------------------------

        cur.execute(
            """
            INSERT INTO customers
            (
                channel,
                user_id,
                sender_name
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
            RETURNING *
            """,
            (
                channel,
                user_id,
                sender_name,
            ),
        )

        customer = cur.fetchone()

        conn.commit()

        cur.close()
        conn.close()

        return {

            "success": True,

            "customer": customer,

            "created": True,
        }

    except Exception as e:

        return {

            "success": False,

            "error": str(e),
        }

import psycopg2
from psycopg2.extras import RealDictCursor


DATABASE_CONFIG = {
    "dbname": "customer_support",
    "user": "postgres",
    "password": "123456",
    "host": "localhost",
}


ALLOWED_FIELDS = [
    "sender_name"
]

@tool
def update_customer(
    customer_id: int,
    updates: dict
) -> dict:

    """
User This tool to Update Customer Profiles
    
    """



    try:

        # -----------------------------
        # Validate updates
        # -----------------------------

        valid_updates = {
            key: value
            for key, value in updates.items()
            if key in ALLOWED_FIELDS
        }


        if not valid_updates:

            return {
                "success": False,
                "message": "No valid fields provided."
            }


        conn = psycopg2.connect(**DATABASE_CONFIG)

        cur = conn.cursor(
            cursor_factory=RealDictCursor
        )


        # -----------------------------
        # Build Dynamic Query
        # -----------------------------

        set_values = []

        values = []


        for field, value in valid_updates.items():

            set_values.append(
                f"{field} = %s"
            )

            values.append(value)


        values.append(customer_id)


        query = f"""
            UPDATE customers
            SET {', '.join(set_values)}
            WHERE id = %s
            RETURNING *
        """


        cur.execute(
            query,
            values
        )


        customer = cur.fetchone()


        if not customer:

            conn.rollback()

            return {
                "success": False,
                "message": "Customer not found."
            }


        conn.commit()


        cur.close()
        conn.close()


        return {

            "success": True,

            "customer": customer
        }


    except Exception as e:

        return {

            "success": False,

            "error": str(e)
        }