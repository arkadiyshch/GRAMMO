from fastapi import FastAPI, Request

print("WEB MODULE LOADED")

app = FastAPI()
from fastapi import FastAPI, Request


@app.get("/123")
async def root():
    return {"status": "ok_123"}


@app.post("/yookassa/webhook")
async def yookassa_webhook(request: Request):
    data = await request.json()

    print("YooKassa webhook:")
    print(data)

    return {"status": "ok"}



@app.get("/yookassa/webhook123")
async def yookassa_webhook_test():
    return {"status": "ok123"}


print("REGISTERED ROUTES:")

for route in app.routes:
    print(route.path, route.methods)