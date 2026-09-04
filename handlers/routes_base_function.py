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
router = Router()
from aiogram.exceptions import TelegramBadRequest


def split_text(text: str, max_length: int = 4000) -> list[str]:
    parts = []

    while len(text) > max_length:
        split_at = text.rfind("\n", 0, max_length)

        if split_at == -1:
            split_at = max_length

        parts.append(text[:split_at])
        text = text[split_at:].lstrip()

    if text:
        parts.append(text)

    return parts


async def delete_active_messages(
    state: FSMContext,
    author: str | None = None,
    type: str | None = None
):
    remaining_messages = []

    data = await state.get_data()
    active_messages = data.get("active_messages", [])

    for item in active_messages:
        author_match = author is None or item.get("author") == author
        type_match = type is None or item.get("type") == type

        if author_match and type_match:
            try:
                await item["message"].delete()
            except TelegramBadRequest:
                pass
        else:
            remaining_messages.append(item)

    await state.update_data(
        active_messages=remaining_messages
    )


async def my_print(state, mes):
    data = await state.get_data()
    debug_mode = data.get("DEBUG_MODE")
    if debug_mode: print(f"{mes} | {state}")
