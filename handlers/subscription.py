#imports
import os
import random
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (CallbackQuery, Message)
import json
import messages as mes
import client as cl
import data.database as db
import keyboards as kb
import json
import asyncio
import payments

from aiogram.exceptions import TelegramBadRequest
import handlers.routes_base_function as rbf
from handlers.routes_base_function import my_print

import states as st
router = Router()

#Главное меню - Подипска Входная точка
@router.callback_query(st.MainStates.subscription , F.data == "user_subscription")
async def user_subscription_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    user_id = data["user_id"]

    subscription = db.get_user_subscription(user_id=user_id)

    if subscription is None:
        await callback.message.edit_text(mes.get_subscribe_mes(subscription), reply_markup=kb.subscription_subscribe_keyboard())

    else:
        await callback.message.edit_text(mes.get_subscribe_mes(subscription).get)



#Оплатить подписку
@router.callback_query(st.MainStates.subscription , F.data == "subscribe")
async def user_subscription_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data["user_id"]

    payment = payments.create_payment(user_id)

    await callback.message.answer(
        "Для оплаты подписки нажмите кнопку ниже:",
        reply_markup=kb.payment_keyboard(
            payment["confirmation_url"]
        )
    )




