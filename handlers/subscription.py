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
@router.callback_query(st.MainStates.main_menu, F.data == "user_subscription")
async def user_subscription_handler(callback: CallbackQuery, state: FSMContext):
    print("im in subscripton")

    await callback.answer()
    data = await state.get_data()
    user_id = data["user_id"]

    await state.set_state(st.MainStates.subscription)
    print(f"state {state}")
    subscription = db.get_user_subscription(user_id=user_id)

    print(f"subscription {subscription}")
    
    if subscription is None:
        await callback.message.edit_text(mes.get_user_subscription_mes(subscription), reply_markup=kb.subscription_subscribe_keyboard())

    else:
        await callback.message.edit_text(mes.get_user_subscription_mes(subscription))

@router.message(st.MainStates.email)
async def process_email(
    message: Message,
    state: FSMContext
):
    email = message.text.strip()

    if "@" not in email or "." not in email:
        await message.answer(
            "Введите корректный email:"
        )
        return

    data = await state.get_data()
    user_id = data["user_id"]

    db.update_user_email(
        user_id=user_id,
        email=email
    )

    await state.set_state(st.MainStates.subscription)

    await message.answer(
        f"Email для чека:\n{email}",
        reply_markup=kb.subscription_payment_keyboard()
    )

@router.callback_query(st.MainStates.subscription, F.data == "subscribe")
async def user_subscription_handler(callback: CallbackQuery, state: FSMContext):
    await user_subscription(callback, state)


async def user_subscription(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    user_id = data["user_id"]

    email = db.get_user_email(user_id)

    if email is None:
        await state.set_state(st.MainStates.email)

        await callback.message.answer(
            "Введите email для оформления чека:"
        )
        return

    await callback.message.answer(
        f"Email для чека:\n{email}",
        reply_markup=kb.subscription_payment_keyboard()
    )

@router.callback_query(st.MainStates.subscription, F.data == "pay_premium")
async def pay_premium_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    user_id = data["user_id"]

    email = db.get_user_email(user_id)

    if email is None:
        await state.set_state(st.MainStates.email)

        await callback.message.answer(
            "Сначала укажите email для оформления чека:"
        )
        return

    payment = payments.create_payment(user_id=user_id,email=email)

    await callback.message.answer("Для оплаты подписки нажмите кнопку ниже:",
        reply_markup=kb.payment_keyboard(payment["confirmation_url"])       
    )
    await state.set_state(st.MainStates.main_menu)


@router.callback_query(st.MainStates.subscription, F.data == "change_email")
async def change_email_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    await state.set_state(st.MainStates.email)

    await callback.message.answer(
        "Введите новый email для оформления чека:"
    )