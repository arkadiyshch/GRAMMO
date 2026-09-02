import os
import uuid
from yookassa import Configuration
from yookassa import Payment
from data import database as db


#YOOKASSA_SHOP_ID = os.getenv("YOOKASSA_SHOP_ID")
#YOOKASSA_SECRET_KEY = os.getenv("YOOKASSA_SECRET_KEY")

Configuration.account_id = os.getenv("YOOKASSA_SHOP_ID")
Configuration.secret_key = os.getenv("YOOKASSA_SECRET_KEY")



#[0] id
#[1] code       = 'premium'
#[2] name       = 'Premium'
#[3] price      = 350
#[4] period     = 1
#[5] daily_limit = 'NULL'
#[6] started_at
#[7] expires_at


def get_return_url():
    res = ""
    local_server = os.getenv("ENV")
    if local_server == "local":
        res = "https://t.me/grammarmarsterBot"

    if local_server == "server":
        res = "https://t.me/grammo_eng_bot"
    
    return res



def create_payment(user_id, email):

    subscription = db.get_subscription("premium")

    if subscription is None:
        raise ValueError("Premium subscription not found")

    subscription_id = subscription[0]
    price = subscription[3]

    idempotence_key = str(uuid.uuid4())

    payment = Payment.create(
        {
            "amount": {
                "value": f"{price:.2f}",
                "currency": "RUB"
            },

            "capture": True,

            "confirmation": {
                "type": "redirect",
                "return_url": get_return_url()
            },

            "description": (
                f"Premium подписка GRAMMO. "
                f"Пользователь: {user_id}."
            ),

            "receipt": {
                "customer": {
                    "email": email
                },
                "items": [
                    {
                        "description": "Premium подписка GRAMMO",
                        "quantity": "1.00",
                        "amount": {
                            "value": f"{price}",
                            "currency": "RUB"
                        },
                        "vat_code": 1,
                        "payment_subject": "service",
                        "payment_mode": "full_prepayment"
                    }
                ]
            }
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