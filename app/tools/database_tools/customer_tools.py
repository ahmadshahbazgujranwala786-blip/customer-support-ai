from sqlalchemy.orm import Session

from app.models.customer import Customer
import uuid

def get_customer_by_user_id(
    db: Session,
    user_id: str,
    channel: str,
) -> Customer | None:
    """
    Get customer by platform user_id + channel.
    """

    return (
        db.query(Customer)
        .filter(
            Customer.user_id == user_id,
            Customer.channel == channel,
        )
        .first()
    )


def create_customer(
    db: Session,
    user_id: str,
    channel: str,
    sender_name: str | None = None,
) -> Customer:
    """
    Create a new customer.
    """

    customer = Customer(
        user_id= user_id,
        channel=channel,
        sender_name=sender_name,
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer


def get_or_create_customer(
    db: Session,
    user_id: str,
    channel: str,
    sender_name: str | None = None,
) -> Customer:
    """
    Returns existing customer or creates one.
    """

    customer = get_customer_by_user_id(
        db=db,
        user_id=user_id,
        channel=channel,
    )

    if customer is None:
        customer = create_customer(
            db=db,
            user_id=user_id,
            channel=channel,
            sender_name=sender_name,
        )

    return customer


def update_customer_name(
    db: Session,
    customer_id: int,
    sender_name: str | None = None
) -> Customer | None:
    """
    Update sender name.
    """

    customer = db.get(Customer, customer_id)

    if customer is None:
        return None

    customer.sender_name = sender_name

    db.commit()
    db.refresh(customer)

    return customer


def delete_customer(
    db: Session,
    customer_id: int,
) -> bool:
    """
    Delete customer.
    """

    customer = db.get(Customer, customer_id)

    if customer is None:
        return False

    db.delete(customer)
    db.commit()

    return True