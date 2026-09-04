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
import handlers.menu as menu

router = Router()

#Главное меню - Подипска Входная точка
@router.callback_query(st.MainStates.main_menu, F.data == "user_subscription")
async def user_subscription_handler(callback: CallbackQuery, state: FSMContext):
    print("im in subscripton")

    await callback.answer()
    data = await state.get_data()
    user_id = data["user_id"]
    active_messages = data.get("active_messages", [])
    

    await state.set_state(st.MainStates.subscription)
    print(f"state {state}")
    subscription = db.get_user_subscription(user_id=user_id)

    print(f"subscription {subscription}")
    await callback.message.edit_text(mes.get_user_subscription_mes(subscription), reply_markup=kb.subscription_subscribe_keyboard(subscription))


@router.message(st.MainStates.email)
async def process_email(message: Message, state: FSMContext):
    data = await state.get_data()
    active_messages = data.get("active_messages")

    email = message.text.strip()
    cur_mes = message
    active_messages.append({
            "message": cur_mes,
            "author": "bot",
            "type": "email"
        })
    await state.update_data(active_messages=active_messages)
    #await rbf.delete_active_messages(state, type="menu")



    if "@" not in email or "." not in email:
        await rbf.delete_active_messages(state, type="email")
        cur_mes = await message.answer("Введите корректный email:")
        active_messages.append({
                    "message": cur_mes,
                    "author": "bot",
                    "type": "email"
                })
        await state.update_data(active_messages=active_messages)
        return

    data = await state.get_data()
    user_id = data["user_id"]

    db.update_user_email(user_id=user_id, email=email)
    await rbf.delete_active_messages(state, type="email")
    await state.set_state(st.MainStates.subscription)

    
    cur_mes = await message.answer(f"Email для чека:\n{email}",reply_markup=kb.subscription_payment_keyboard())

    active_messages.append({
        "message": cur_mes,
        "author": "bot",
        "type": "email"
    })
    await state.update_data(active_messages=active_messages)
   


@router.callback_query(st.MainStates.subscription, F.data == "subscribe")
async def user_subscription_handler(callback: CallbackQuery, state: FSMContext):
    await user_subscription(callback, state)


async def user_subscription(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    user_id = data["user_id"]
    active_messages = data.get("active_messages")

    email = db.get_user_email(user_id)

    if email is None:
        await state.set_state(st.MainStates.email)

        await callback.message.answer(
            "Введите email для оформления чека:"
        )
        return

    cur_mes = await callback.message.answer(f"Email для чека:\n{email}",reply_markup=kb.subscription_payment_keyboard())
    
    active_messages.append({
        "message": cur_mes,
        "author": "bot",
        "type": "email"
    })
    await state.update_data(active_messages=active_messages)


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

    print("state:", await state.get_state())
    await callback.message.answer("Для оплаты подписки нажмите кнопку ниже:",
        reply_markup=kb.payment_keyboard(payment["confirmation_url"])       
    )
    await state.set_state(st.MainStates.main_menu)


@router.callback_query(st.MainStates.subscription, F.data == "change_email")
async def change_email_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    active_messages = data.get("active_messages")

    await state.set_state(st.MainStates.email)

    cur_mes = await callback.message.answer("Введите новый email для оформления чека:")
    active_messages.append({
                "message": cur_mes,
                "author": "bot",
                "type": "email"
            })
    await state.update_data(active_messages=active_messages)


#Возврат в главное меню из подписки
@router.callback_query(st.MainStates.subscription, F.data == "back")
async def subscription_back_handler(callback: CallbackQuery, state: FSMContext):
    await subscription_back(callback, state)

#Возврат в главное меню из подписки
@router.callback_query(st.MainStates.main_menu, F.data == "back")
async def subscription_back_handler(callback: CallbackQuery, state: FSMContext):
    await subscription_back(callback, state)


async def subscription_back(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    user_id = data["user_id"]  

    await state.set_state(st.MainStates.main_menu)
    rbf.delete_active_messages(state, author="user")
    rbf.delete_active_messages(state, author="bot")
    await callback.message.answer("Главное меню", reply_markup=await kb.main_menu_keyboard(user_id))
    
