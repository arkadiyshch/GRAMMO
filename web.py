from fastapi import FastAPI, Request, HTTPException
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

        try:
            result = db.process_successful_payment(
                yookassa_payment_id
            )

            print("Payment processing:", result)

        except Exception as e:
            print(f"Payment processing error: {e}")

            raise HTTPException(
                status_code=500,
                detail="Payment processing failed"
            )

    return {"status": "ok"}

##################################################################
print("REGISTERED ROUTES:")
for route in app.routes:
    print(route.path, route.methods)
##################################################################