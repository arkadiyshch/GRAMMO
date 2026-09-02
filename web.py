from fastapi import FastAPI, Request
import data.database as db

print("WEB MODULE LOADED")

app = FastAPI()
from fastapi import FastAPI, Request

@app.post("/yookassa/webhook")
async def yookassa_webhook(request: Request):
    data = await request.json()

    print("YooKassa webhook:")
    print(data)

    event = data.get("event")

    if event == "payment.succeeded":

        yookassa_payment_id = data["object"]["id"]
        payment = db.get_payment_by_yookassa_id(yookassa_payment_id)

        if payment is None:
            print(
                f"Payment not found in DB: "
                f"{yookassa_payment_id}"
            )
            return {"status": "ok"}

        print("Payment found:", payment)

        db.mark_payment_succeeded(yookassa_payment_id)

    return {"status": "ok"}


##################################################################
print("REGISTERED ROUTES:")
for route in app.routes:
    print(route.path, route.methods)
##################################################################