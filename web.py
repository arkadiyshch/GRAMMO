from fastapi import FastAPI, Request

app = FastAPI()

import os
import uvicorn

from fastapi import FastAPI, Request

app = FastAPI()


@app.post("/yookassa/webhook")
async def yookassa_webhook(request: Request):
    data = await request.json()

    print("YooKassa webhook:")
    print(data)

    return {"status": "ok"}


@app.get("/")
async def root():
    return {"status": "ok"}