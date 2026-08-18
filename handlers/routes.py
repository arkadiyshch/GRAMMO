#imports
import os
import random

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    Message
)
import json
import messages as messages

from client import (
    get_sentence, 
    generate_sentence,
    check_answer, 
    format_check_result
)
from dataBase.database import (
    add_sentence,
    add_user,
    get_current_user_level,
    get_groups,
    get_topics,
    save_user_level,
    get_level_name,
    save_user_answer, 
    get_topics_count
)
from keyboards import (
    blitz_groups_keyboard,
    blitz_topics_keyboard,
    user_level_keyboard,
    welcome_keyboard,
    main_menu_keyboard,
    finish_blitz_keyboard
)
from states import BlitzState

router = Router()
TOTAL_QUESTIONS = 10

#[START]
@router.message(F.text == "/start")
async def welcome(
    message: Message,
    state: FSMContext
    ):
    await state.clear()
    user_id = message.from_user.id
    await state.update_data(user_id=user_id)
    
    add_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username
    )

    level = get_current_user_level(user_id)
    print(level)
    welcome_message =messages.get_welcome_message()# os.getenv("WELCOME_MESSAGE")
    await message.answer(welcome_message)
    if level is None:
        await state.update_data(first_launch=True)
        await message.answer("Попробуем?", reply_markup=welcome_keyboard())
        
    else:
        await state.update_data(first_launch=False)
        await message.answer("Начинаем тренировку?", reply_markup=main_menu_keyboard(level))
        

# [НАЧАТЬ БЛИЦ]
@router.callback_query(F.data == "start_blitz")
async def start_blitz(    callback: CallbackQuery, state: FSMContext):
    await callback.answer()
     
    await start_blitz_flow(
        callback,
        callback.message,
        state
    )

async def start_blitz_flow(callback: CallbackQuery, message: Message, state: FSMContext ):

    data = await state.get_data()
    print(data)
    await state.update_data(
            #Настройки блица
            #level_id =  level_id,
            #group_id = x, 
            #topic_id = x,
            #difficulty = 1,
            
            # --- прогресс блица ---
            total_questions =TOTAL_QUESTIONS,
            current_question = 0,
    
            #Вопросы (id, text) и ответы
            questions={},
            answers={}
            )

    user_id = callback.from_user.id#data["user_id"]
    level_id = get_current_user_level(user_id)

    if level_id is None:
        await state.set_state(BlitzState.choosing_level)
        await callback.message.edit_text("Какой у вас уровень?", reply_markup=user_level_keyboard())
        return
    
   
    await state.update_data(
            user_id = user_id,
            #Настройки блица
            level_id =  level_id,
            #group_id = x, 
            #topic_id = x,
            difficulty = 1,
            
            # --- прогресс блица ---
            #total_questions =TOTAL_QUESTIONS,
            #current_question = 0,
    
            #Вопросы (id, text) и ответы
            #questions={},
            #answers={}
            )

    groups = get_groups(level_id=level_id)
    await state.set_state(BlitzState.choosing_group)
    await callback.message.edit_text("Что хочешь потренировать?", reply_markup=blitz_groups_keyboard(groups))


#change_level
#[ИЗМЕНИТЬ УРОВЕНЬ]
@router.callback_query(F.data.startswith("change_level"))
async def change_level(callback: CallbackQuery,state: FSMContext):
    await state.set_state(BlitzState.choosing_level)
    await callback.message.edit_text("Какой у вас уровень?", reply_markup=user_level_keyboard())

#[ВЫБОР УРОВНЯ]
@router.callback_query(F.data.startswith("level_"))
async def choose_level(callback: CallbackQuery,state: FSMContext):
    data = await state.get_data()
    user_id = callback.from_user.id

    level_id = callback.data.replace("level_",""    )
    save_user_level(user_id=user_id, level_id=level_id)
    await state.update_data(
        #Настройки блица
        level_id =  level_id,
        #group_id = x, 
        #topic_id = x,
        difficulty = 1,
        
        # --- прогресс блица ---
        total_questions =TOTAL_QUESTIONS,
        current_question = 0,

        #Вопросы (id, text) и ответы
        questions={},
        answers={}
        )
    await callback.answer()

    level = get_current_user_level(user_id)
    first_launch = data["first_launch"]
    #Если это первый запуск, то сразу идем в тест, если нет, то в главное меню
    
    if first_launch:
        await start_blitz_flow(
                callback,
                callback.message,
                state
            )       
    else:        
        await callback.message.edit_text("Начинаем тренировку?", reply_markup=main_menu_keyboard(level))

#[ВЫБОР ГРУППЫ]   
@router.callback_query(BlitzState.choosing_group, F.data.startswith("blitz_group_"))
async def blitz_group(callback: CallbackQuery, state: FSMContext):
    group_id = int(callback.data.split("_")[-1])
   

    data = await state.get_data()
    level_id = data["level_id"]
    user_id = callback.from_user.id
    if group_id==0:
        await state.update_data(
            #Настройки блица
            #level_id =  level_id,
            group_id = 0, 
            topic_id = 0,
            #difficulty = 1,
            
            # --- прогресс блица ---
            total_questions =TOTAL_QUESTIONS,
            current_question = 0,

            #Вопросы (id, text) и ответы
            #questions={},
            #answers={}
        )


        await state.set_state(BlitzState.answering)
        await callback.answer()
        await get_blitz_question(callback.message, state, user_id)

    else:
        topics = get_topics(parent_id=group_id, level_id=level_id)

        await state.update_data(
            #Настройки блица
            #level_id =  level_id,
            group_id = group_id, 
            #topic_id = x,
            #difficulty = 1,
            
            # --- прогресс блица ---
            total_questions =TOTAL_QUESTIONS,
            current_question = 0,       
            )
        
        await state.set_state(BlitzState.choosing_topic)
        await callback.answer()

        topics = get_topics(group_id, level_id)
        topics_count = len(topics)
        
        if topics_count> 1:
            await callback.message.edit_text("Выберите подтему:",reply_markup=blitz_topics_keyboard(topics))
        elif topics_count == 1:
            user_id =  callback.from_user.id    
            topic_id = topics[0][0]
            await state.set_state(BlitzState.answering)
            await callback.answer()

            await state.update_data(topic_id = topic_id)
            await get_blitz_question(callback.message, state, user_id)
        else:
            return


# [ВЫБОР ТОПИКА]
@router.callback_query(BlitzState.choosing_topic, F.data.startswith("blitz_topic_"))
async def blitz_choose_topic(callback: CallbackQuery, state: FSMContext):
    await state.update_data(
        topic_id=int(callback.data.split("_")[-1]), 
        counter=0
        ) 


    await state.update_data(
            #Настройки блица
            #level_id =  level_id,
            #group_id = x, 
            topic_id = callback.data.split("_")[-1],
            #difficulty = 1,
            
            # --- прогресс блица ---
            #total_questions =TOTAL_QUESTIONS,
            #current_question = 0,
    
            #Вопросы (id, text) и ответы
            #questions={},
            #answers={}
            )


    user_id =  callback.from_user.id
    await state.set_state(BlitzState.answering)
    await callback.answer()
    await get_blitz_question(callback.message, state, user_id)

#[НАЗАД] к группам
@router.callback_query(BlitzState.choosing_topic, F.data == "back")
async def back_to_groups(callback: CallbackQuery,state: FSMContext):
    data = await state.get_data()
    level_id = data["level_id"]
    groups = get_groups(level_id=level_id)
    await state.set_state(BlitzState.choosing_group)
    await callback.answer()
    await callback.message.edit_text("Что хочешь потренировать?", reply_markup=blitz_groups_keyboard(groups))

#[НАЗАД] в главное меню
@router.callback_query(BlitzState.choosing_group, F.data == "back")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    #await state.clear()
    await callback.answer()

    user_id =  callback.from_user.id
    level = get_current_user_level(user_id)
    await callback.message.edit_text("Начинаем тренировку?", reply_markup=main_menu_keyboard(level))

# [ПОЛУЧИТЬ ВОПРОС ДЛЯ ПЕРЕВОДА]  
#@router.callback_query(BlitzState.answering)
async def get_blitz_question(message: Message, state: FSMContext, user_id: int):
        
    data = await state.get_data()

    _level_id = data["level_id"]
    _difficulty = data["difficulty"]
    _group_id = data["group_id"]
    _topic_id=data["topic_id"]
    _current_question=data["current_question"]
    _total_question=data["total_questions"]
        
    _questions = data["questions"]
    

    # ОПРЕДЕЛЯЕМ ГРУППУ И ТОПИК
    #Group_id = 0  -> Любая группа с любыми топиками
    #Topic_id = 0  -> Топики в перемешку в рамках группы 
    
    if _group_id == 0: _group_id = random.choice(get_groups(level_id=_level_id))[0]
  
    topics = get_topics(parent_id=_group_id, level_id=_level_id)

    a = random.choice(get_topics(parent_id=_group_id, level_id=_level_id), )[0] 
    
    if _topic_id == 0: _topic_id = a #random.choice(get_topics(parent_id=_group_id, level_id=_level_id), )[0] 
    topic_id = a

    _current_question += 1

    if _current_question == 1:
        await message.answer(messages.get_start_bliz_message(_group_id, topic_id ))

   

    sentence = await get_sentence(user_id=user_id, level_id=_level_id, difficulty=_difficulty, group_id=_group_id, topic_id = topic_id)


    _questions[_current_question]={
                "id": sentence["id"],
                "text": sentence["text"],
                "answer": ""
            }
    
    await state.update_data(
        #Настройки блица
        #level_id =  level_id,
        group_id = _group_id, 
        topic_id = _topic_id,
        #difficulty = 1,
        
        # --- прогресс блица ---
        #total_questions =TOTAL_QUESTIONS,
        current_question = _current_question,

        #Вопросы (id, text) и ответы
        questions = _questions,
        #answers=[]
        )

    
    await message.answer(
        f"<b>Вопрос {_current_question} из {_total_question}</b>\n\n"
      
        f"<i>{sentence['text']}</i>",
        reply_markup=finish_blitz_keyboard()
)

@router.message(BlitzState.answering)
async def blitz_answer(
    message: Message,
    state: FSMContext
):
   
    data = await state.get_data()
    user_answer = message.text.strip()

    current_question = data["current_question"]
    total_questions = data.get(
        "total_questions",
        TOTAL_QUESTIONS
    )

    questions = data["questions"]

    # --------------------------------------------------
    # Получаем текущий вопрос
    # --------------------------------------------------

    current_question_data = questions[current_question]

    current_sentence_id = current_question_data["id"]
    current_sentence = current_question_data["text"]

    #print("Номер вопроса:", current_question)
    #print("ID предложения:", current_sentence_id)
    #print("Русское предложение:", current_sentence)
    #print("Ответ пользователя:", user_answer)

    questions[current_question]["answer"] = user_answer

    #Делаем ии проверку
    await message.answer(
        "Проверяю ответ..."
    )

    ai_result = await check_answer(
        russian_sentence=current_sentence,
        user_answer=user_answer
    )

    # --------------------------------------------------
    # Сохраняем результат проверки
    # --------------------------------------------------

    questions[current_question]["ai_answer"] = ai_result

    await state.update_data(
        questions=questions
    )

    #Идем дальше

    await state.update_data(
        questions=questions
    )

    
    save_user_answer(
           user_id=message.from_user.id,
           sentence_id=current_sentence_id,
           user_answer=user_answer,
           ai_answer = json.dumps(
                ai_result,
                ensure_ascii=False
            )
       )

    await message.answer(
         format_check_result(ai_result)
    )

    if current_question >= total_questions:

        await finish_blitz(
            message,
            state
        )

        return

    # --------------------------------------------------
    # Переходим к следующему вопросу
    # --------------------------------------------------
    user_id=message.from_user.id
    await get_blitz_question(
        message,
        state, 
        user_id
    )



@router.callback_query(
    BlitzState.answering,
    F.data == "finish_blitz"
)
async def finish_blitz_callback(
    callback: CallbackQuery,
    state: FSMContext
):
    await callback.answer()
    user_id = callback.from_user.id
    await finish_blitz(
        callback.message,
        state,
        user_id
    )


async def finish_blitz(
    message: Message,
    state: FSMContext,
    user_id: int
):
    data = await state.get_data()

    questions = data.get("questions", {})

    answered_questions = []

    for question_number, question in questions.items():

        if question.get("answer"):
            answered_questions.append({
                "question_number": question_number,
                "sentence_id": question["id"],
                "sentence": question["text"],
                "user_answer": question["answer"]
            })

    #if not answered_questions:
    #    await message.answer(
    #        "Вы не ответили ни на один вопрос."
    #    )
    #    await state.clear()
    #    return

    # Здесь потом:
    # results = await analyze_blitz_answers(answered_questions)

    await message.answer(
        "Блиц завершён!\n\n"
        f"Выполнено заданий: {len(answered_questions)}"
    )

    #await state.clear()

       # --------------------------------------------------
    # Возвращаемся в главное меню
    # --------------------------------------------------

    level = get_current_user_level(user_id)

    await message.answer(
        "Начинаем тренировку?",
        reply_markup=main_menu_keyboard(level)
    )


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