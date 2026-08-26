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

#from states import BlitzState

router = Router()
TOTAL_QUESTIONS = 10

        


# ============================================================
# ПРОЧИЕ ФУНКЦИИ
# ============================================================


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