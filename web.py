from fastapi import FastAPI, Request

app = FastAPI()
from fastapi import FastAPI, Request

app = FastAPI()


@app.get("/")
async def root():
    return {"status": "ok"}


@app.post("/yookassa/webhook")
async def yookassa_webhook(request: Request):
    data = await request.json()

    print("YooKassa webhook:")
    print(data)

    return {"status": "ok"}