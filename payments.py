import os
import uuid
from yookassa import Configuration
from yookassa import Payment
from data import database as db


YOOKASSA_SHOP_ID = os.getenv("YOOKASSA_SHOP_ID")
YOOKASSA_SECRET_KEY = os.getenv("YOOKASSA_SECRET_KEY")



def get_return_url():
    res = ""
    local_server = os.getenv("ENV")
    if local_server == "local":
        res = "https://t.me/grammarmarsterBot"

    if local_server == "server":
        res = "https://t.me/grammo_eng_bot"
    
    return res



def create_payment(user_id):

    subscription = db.get_subscription("premium")

    if subscription is None:
        raise ValueError("Premium subscription not found")

    subscription_id = subscription["id"]
    price = subscription["price"]

    idempotence_key = str(uuid.uuid4())

    payment = Payment.create(
        {
            "amount": {
                "value": f"{price}",
                "currency": "RUB"
            },
            "capture": True,
            "confirmation": {
                "type": "redirect",
                "return_url": get_return_url()
            },
            "description": (
                f"Premium подписка GRAMMO. "
                f"Пользователь: {user_id}. "

)
        },
        idempotence_key
    )

    db_payment_id = db.save_payment(
        user_id=user_id,
        subscription_id=subscription_id,
        yookassa_payment_id=payment.id,
        amount=price,
        currency="RUB",
        status=payment.status
    )

    return {
        "payment_id": db_payment_id,
        "yookassa_payment_id": payment.id,
        "confirmation_url": payment.confirmation.confirmation_url
    }