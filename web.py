from fastapi import FastAPI, Request, HTTPException
import data.database as db
import bot_instance
import keyboards as kb


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
            result = db.process_successful_payment(yookassa_payment_id)
            print("Payment processing:", result)

            #Возврат в главное меню
            user_id = result["user_id"]


            await bot_instance.bot.send_message(
                chat_id=user_id,
                text="Оплата прошла успешно.\n\nГлавное меню",
                reply_markup=await kb.main_menu_keyboard(...)
            )
            
            
            
            
            #await state.set_state(st.MainStates.main_menu)
            
            #cur_mes = await message.answer("Главное меню", reply_markup=await kb.main_menu_keyboard(state))
            #active_messages.append({
            #            "message" : cur_mes,
            #            "author": "bot",
            #            "type": "menu"
            #        })     


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