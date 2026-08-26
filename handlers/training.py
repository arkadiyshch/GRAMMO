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
from aiogram.exceptions import TelegramBadRequest

import states as st
router = Router()
TOTAL_QUESTIONS = 10
import prompts as p




async def tarining_start(callback: CallbackQuery, state: FSMContext):
    print("tarining_start")
    data = await state.get_data()
    level_id = data.get("level_id")
    user_id = data.get("user_id")
    grammar_topic_id =  data.get("grammar_topic_id")
    lexical_topic_id =  data.get("lexical_topic_id")
    difficulty_id = data.get("difficulty_id")
    welcome_mode = data.get("welcome_mode")

    print(f"welcome_mode {welcome_mode}")
    sentece_cont = TOTAL_QUESTIONS
    if welcome_mode:sentece_cont = 3
    

    await state.update_data(current_sentence = 0, total_sentence = sentece_cont)

    # Приветствие
    await callback.message.answer(
        f"Начинаем тренировку!\n\n"
        f"Задания скоро появятся. Всего их будет: {sentece_cont}\n"
        f"Отправляйте перевод прямо в чат."
    )


    progress_message = await callback.message.answer(make_progress_bar(0, sentece_cont))
    await state.update_data(progress_message=progress_message)
    
    prompt = await p.get_sentences_prompt(user_id=user_id, level_id=level_id, difficulty=difficulty_id, grammar_topic_id=grammar_topic_id, lexical_topic_id=lexical_topic_id,  sentence_count= sentece_cont, welcome_mode = welcome_mode)
    sentences = await cl.generate_sentences(prompt)

    
    
    sentences_JSON = json.loads(sentences)
    save_sentences(sentences_data=sentences_JSON, level_id=level_id, grammar_topic_id=grammar_topic_id, lexical_topic_id=lexical_topic_id, difficulty_id=difficulty_id, sentence_type=0)

    await state.update_data(sentences = sentences_JSON)        
    await show_next_sentence(callback.message, state)


def make_progress_bar(current: int, total: int, length: int = 10) -> str:
    filled = round(length * current / total)
    empty = length - filled

    mes = ""
    if current<total:
        mes = "Выполнено заданий:"
    else:
        mes = "Вы выполнили все задания"

    return (
        f"{mes}\n\n"
        f"{'█' * filled}{'░' * empty}  {current}/{total}"
    )


async def show_next_sentence(message: Message, state: FSMContext):

    data = await state.get_data()
    await delete_prev_messages(state)

    
    current_sentence =data.get("current_sentence")
    total_sentence =data.get("total_sentence") 
    sentences = data["sentences"]   

    if current_sentence>0:
        progress_message = data["progress_message"]

        try:
            await progress_message.edit_text(make_progress_bar(current_sentence, total_sentence, 10))
        except TelegramBadRequest as e:
                if "message is not modified" in str(e):
                    pass
                else:
                    raise


        
    
    
    await state.update_data(tips_message_2=None)

    if current_sentence == total_sentence:
        await finish_training(message, state)

    else:
        current_sentence +=1
        await state.update_data(current_sentence = current_sentence, tips_showed = False)
        mes = f"{current_sentence}. {sentences['sentences'][current_sentence - 1]['question']}"
        sentence_message_1 = await message.answer(mes,  reply_markup=kb.sentence_answer_keyboard())
        await state.update_data(sentence_message_1=sentence_message_1)
        await state.set_state(st.MainStates.bliz_answer)

#Обработка ответа пользвоателя
@router.message(st.MainStates.bliz_answer)
async def training_answer_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data["user_id"]
    sentences = data["sentences"]        
    current_sentence = data["current_sentence"]
    total_sentence =data.get("total_sentence") 
    answer_sentence_3 = message
    await state.update_data(answer_sentence_3 = answer_sentence_3)

    user_answer = message.text.strip()
    question = sentences['sentences'][current_sentence-1]["question"]
    question_id = sentences['sentences'][current_sentence-1]["question_id"] 

    # Сохраняем ответ в state
    ai_result = await cl.check_answer(russian_sentence=question, user_answer=user_answer)
    sentences['sentences'][current_sentence-1]["answer"] = user_answer
    sentences['sentences'][current_sentence-1]["ai_result"] = ai_result

    
    await state.update_data(sentences=sentences)
    
    db.save_user_answer(
        user_id=message.from_user.id,
        sentence_id=question_id,
        user_answer=user_answer,
        ai_answer = json.dumps(
                ai_result,
                ensure_ascii=False
            )
    )

    feedback_message_4 = await message.answer(cl.format_check_result(ai_result),reply_markup=kb.next_sentence_keyboard())

    await state.update_data(feedback_message_4=feedback_message_4)
    
    # Последний вопрос?
    if current_sentence < total_sentence:
        a = True
    else:
        finish_training(message, state)




    
async def delete_prev_messages(state: FSMContext):
    data = await state.get_data()
    sentence_message_1 = data.get("sentence_message_1")
    tips_message_2 = data.get("tips_message_2")
    answer_sentence_3 = data.get("answer_sentence_3")
    feedback_message_4 = data.get("feedback_message_4")

    if sentence_message_1 is not None: await sentence_message_1.delete()
    if tips_message_2 is not None: await tips_message_2.delete()
    if answer_sentence_3 is not None: await answer_sentence_3.delete()
    if feedback_message_4 is not None: await feedback_message_4.delete()

    await state.update_data(sentence_message_1 = None)
    await state.update_data(tips_message_2 = None)
    await state.update_data(answer_sentence_3 = None)
    await state.update_data(feedback_message_4 = None)



#Показываем подсказки
@router.callback_query(st.MainStates.bliz_answer , F.data == "answer_tips")
async def answer_show_tips_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()    
    #await state.set_state(st.MainStates.bliz_tips)
    
    data = await state.get_data()
    tips_message_2 =data.get("tips_message_2")

    print(f"tips_message_2 {tips_message_2}")
    if tips_message_2 is None:
        total_sentence = data["total_sentence"]
        sentences = data["sentences"]        
        current_sentence = data["current_sentence"]
        tips = sentences['sentences'][current_sentence - 1]['tips']
        new_mes = await callback.message.answer(format_tips(tips))
        await state.update_data(tips_message_2=new_mes)
    else:
        await tips_message_2.delete()
        await state.update_data(tips_message_2=None)

        
    

    #if current_sentence==total_sentence:
    #    a = True
        #выход из тренировки

#Следующее предложение
@router.callback_query(st.MainStates.bliz_answer , F.data == "next_sentence")
async def answer_skip_answer_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer() 
    await show_next_sentence(callback.message, state)  

#Обрабатываем событие заввершения
@router.callback_query(st.MainStates.bliz_answer , F.data == "finish_training")
async def answer_finish_training_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    level_id = data["level_id"]
    
    await finish_training(callback.message, state)

    
    
#Выводим общий итог - комментарий
async def finish_training(message: Message, state: FSMContext):
    await delete_prev_messages(state)
    data = await state.get_data()
    level_id = data["level_id"]
    sentences = data["sentences"]   
    welcome_mode = data["welcome_mode"]  

    current_sentence =data.get("current_sentence")
    total_sentence =data.get("total_sentence") 

    #Обновляем прогресс бар
    if current_sentence>0:
        progress_message = data["progress_message"]

        try:
            await progress_message.edit_text(make_progress_bar(current_sentence, total_sentence, 10))
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                pass
            else:
                raise





    analysis_data = prepare_training_analysis_data(sentences["sentences"])
    analized_result = await cl.analyze_training(analysis_data)

    if welcome_mode:
        await message.answer(format_training_analysis(analized_result))  
        #await message.answer("Вы увидели не только правильные ответы, но и свои ошибки с объяснениями.")   
        await message.answer("Вот так работает GRAMMO\n Переводите предложение -> Получаете обратную связь -> Становитесь лучше вместе с GRAMMO\n\n")  
        await message.answer("Хотите продолжить?", reply_markup=kb.yes2_keyboard()) 
    else:
        await message.answer(format_training_analysis(analized_result),  reply_markup=kb.finish_training_keyboard())

#Возврат в галвное меню
@router.callback_query(st.MainStates.bliz_answer , F.data == "yes2")
async def yes2_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(mes.get_onboard_mes(), reply_markup=kb.onboard_keyboard()) 


@router.callback_query(F.data.startswith("onboard_pay"))
async def onboard_pay_handler(callback: CallbackQuery, state: FSMContext):
    print("im here pay in onboard")

    await callback.answer()
    data = await state.get_data()
    level_id = data["level_id"]

    stop1 = True
    if F.data == "onboard_pay":
        await callback.message.answer("Позддравляем с умпешным оформление подписки. Желаем хорошей тренировки.")
        stop1 = False

    if F.data == "onboard_free":
        await callback.message.answer("Хорошо. вы всегда сможете подключить полный доступ позже.")
        stop1 = False

    if stop1: return

   

    await state.update_data(welcome_mode = False)
    await state.set_state(st.MainStates.main_menu,)
    print(state)
    print(state.get_data())
    
    await callback.message.answer("Главное меню", reply_markup=kb.main_menu_keyboard(level_id))

  
    
    
    
#Возврат в галвное меню
@router.callback_query(st.MainStates.bliz_answer , F.data == "training_main_menu")
async def answer_back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    level_id = data["level_id"]
    await state.set_state(st.MainStates.main_menu)
    await callback.message.answer("Главное меню", reply_markup=kb.main_menu_keyboard(level_id))


def format_tips(tips):
    if not tips:
        return "Для этого предложения подсказок нет."

    text = "Подсказки:\n\n"

    for tip in tips:
        text += f"• {tip['en']} — {tip['ru']}\n"

    return text

# Готовим данные для сводного итогового анализа
def prepare_training_analysis_data(sentences: list) -> list:
    analysis_data = []

    for sentence in sentences:
        result = sentence.get("ai_result")

        if not result: continue

        item = {
            "score": result.get("total_score", 0),
            "errors": []
        }

        # Grammar
        for error in result.get("grammar", {}).get("errors", []):
            item["errors"].append({
                "category": "grammar",
                "wrong": error.get("wrong", ""),
                "correct": error.get("correct", "")
            })

        # Vocabulary
        for comment in result.get("vocabulary", {}).get("comments", []):
            item["errors"].append({
                "category": "vocabulary",
                "comment": comment
            })

        # Accuracy
        for comment in result.get("accuracy", {}).get("comments", []):
            item["errors"].append({
                "category": "accuracy",
                "comment": comment
            })

        # Spelling
        for error in result.get("spelling", {}).get("errors", []):
            item["errors"].append({
                "category": "spelling",
                "wrong": error.get("wrong", ""),
                "correct": error.get("correct", "")
            })

        # Добавляем только если есть ошибки
        if item["errors"]: 
            analysis_data.append(item)
        else:
            # Даже если ошибок нет, score полезен для общей оценки
            analysis_data.append({
                "score": item["score"],
                "errors": []
            })

    return analysis_data


def format_training_analysis(result: dict) -> str:
    text = "<b>Результат тренировки</b>\n\n"

    # Общая оценка
    text += (
        f"<b>Оценка: "
        f"{result.get('overall_score', 0)}/10</b>\n\n"
    )

    # Что подтянуть
    weaknesses = result.get("weaknesses", [])

    if weaknesses:
        text += "<b>Что подтянуть:</b>\n"

        for item in weaknesses:
            topic = item.get("topic", "")
            frequency = item.get("frequency", 0)

            if topic:
                text += f"• {topic}"

                if frequency:
                    text += f" ({frequency}×)"

                text += "\n"

        text += "\n"

    # Что потренировать
    what_to_practice = result.get("what_to_practice", [])

    if what_to_practice:
        text += "<b>Потренировать:</b>\n"

        for item in what_to_practice:
            text += f"• {item}\n"

        text += "\n"

    # Что получается хорошо
    strengths = result.get("strengths", "")

    if strengths:
        text += "<b>Получается хорошо:</b>\n"
        text += f"{strengths}\n\n"

    # Что делать дальше
    final_recommendation = result.get("final_recommendation", "")

    if final_recommendation:
        text += "<b>Что делать дальше:</b>\n"
        text += final_recommendation

    return text




def save_sentences(
    sentences_data: dict,
    level_id: int,
    grammar_topic_id: int,
    lexical_topic_id: int | None,
    difficulty_id: int,
    sentence_type: int = 0
):
    sentences = sentences_data["sentences"]

    for item in sentences:
        question = item["question"]

        print(f"level_id {level_id}")
        print(f"grammar_topic_id {grammar_topic_id}")
        print(f"lexical_topic_id {lexical_topic_id}")
        print(f"difficulty_id {difficulty_id}")
        print(f"sentence_type {sentence_type}")

        question_id = db.save_sentence(
            sentence=question,
            level_id=level_id,
            grammar_topic_id=grammar_topic_id,
            lexical_topic_id=lexical_topic_id,
            difficulty_id=difficulty_id,
            sentence_type=sentence_type
        )

        item["question_id"] = question_id

    return sentences_data







async def get_sentences(
    user_id: int,
    level_id: int,
    difficulty: int,
    grammar_topic_id: int,
    lexical_topic_id: int    
):


    generated_sentence = await generate_sentence(
        level=db.get_level_name(level_id),
        difficulty=difficulty,
        group =db.get_group_name(group_id),
        topic=db.get_topic_name(topic_id),        
        previous_sentences=previous_sentences
    )

    
        

    # 3. Сохраняем его в БД
    sentence_id = add_sentence(
        sentence=generated_sentence,
        level_id=level_id,
        topic_id=topic_id,
        sentence_type=0
    )

    # 4. Возвращаем предложение
    return {
        "id": sentence_id,
        "text": generated_sentence
    }



async def get_training_question(message: Message, state: FSMContext, user_id: int):
        
    data = await state.get_data()
    level_id = data["level_id"]
    difficulty = data["difficulty"]
    grammar_topic_id=data["grammar_topic_id"]
    lexical_topic_id=data["lexical_topic_id"]
    current_question=data["current_question"]
    total_question=data["total_questions"]
        
    #_questions = data["questions"]
    




    sentence = await cl.get_sentence(user_id=user_id, level_id=_level_id, difficulty=_difficulty, group_id=_group_id, topic_id = topic_id)


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
        #f"<b>Задание  {_current_question} из {_total_question}</b>\n\n"
        f"<b>Задание  {_current_question}</b>\n\n"

        f"<i>{sentence['text']}</i>",
        reply_markup=kb.finish_blitz_keyboard()
)





##########################################################Дальше старок















#[Проверка уровня]
@router.callback_query(F.data.startswith("bliz_prepare_1_check_level"))
async def bliz_prepare_1_check_level(callback: CallbackQuery, state: FSMContext):
    await callback.answer()     
    data = await state.get_data()
    level_id = data["level_id"]

    if level_id is None:
        await state.set_state(st.MainStates.choosing_level)
        await callback.message.edit_text("Какой у вас уровень?", reply_markup=kb.user_level_keyboard())
        return

    #Переход к группам       
    groups = db.get_groups(level_id=level_id)
    await state.set_state(st.MainStates.choosing_grammar_topic)
    await callback.message.edit_text("Что хочешь потренировать?", reply_markup=kb.blitz_groups_keyboard(groups))



##Показать список грамматических групп
async def show_groups(callback: CallbackQuery, state: FSMContext):
    await callback.answer()     
    data = await state.get_data()
    level_id = data["level_id"]

    #Переход к группам       
    groups = db.get_groups(level_id=level_id)
    await callback.message.edit_text("Что хочешь потренировать?", reply_markup=kb.blitz_groups_keyboard(groups))
        

    



#[ВЫБОР ГРУППЫ]   
@router.callback_query(st.MainStates.choosing_grammar_topic)
async def show_groups_handler1(callback: CallbackQuery, state: FSMContext):
    await callback.answer()   
    await show_groups_(callback, state)
    

async def show_groups_(callback: CallbackQuery, state: FSMContext):      
    group_id = int(callback.data.split("_")[-1])  #Первичное
    await state.update_data(group_id = group_id)

    data = await state.get_data()
    level_id = data["level_id"]
    user_id = data["user_id"]
    if group_id==0:
        await state.set_state(st.MainStates.bliz_ask)
        await state.update_data(topic_id = 0, total_questions = TOTAL_QUESTIONS, current_question = 0)
        await get_blitz_question(callback.message, state, user_id)

    else:
        topics = db.get_topics(parent_id=group_id, level_id=level_id)
        topics_count = len(topics)
                
        
        #await state.set_state(st.MainStates.bliz_choose_gramma_topic)
        
        
        if topics_count> 1:
            await state.set_state(st.MainStates.choosing_grammar_topic)
            await callback.message.edit_text("Выберите подтему:",reply_markup=kb.blitz_topics_keyboard(topics))
            
        elif topics_count == 1:
            topic_id = topics[0][0]
            await state.set_state(st.MainStates.bliz_answer)
            await callback.answer()

            await state.update_data(topic_id =topic_id, total_questions =TOTAL_QUESTIONS, current_question = 0)
            await get_blitz_question(callback.message, state, user_id)
        else:
            return


# [ВЫБОР ТОПИКА]
@router.callback_query(st.MainStates.choosing_grammar_topic, F.data.startswith("blitz_topic_"))
async def blitz_choose_topic(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    topic_id = callback.data.split("_")[-1],
    data = await state.get_data()
    user_id = data["user_id"]

    await state.set_state(st.MainStates.bliz_answer)    
    await state.update_data( topic_id =topic_id, total_questions =TOTAL_QUESTIONS, current_question = 0)                
    await get_blitz_question(callback.message, state, user_id)

#[НАЗАД] к группам
@router.callback_query(st.MainStates.choosing_grammar_topic, F.data == "back")
async def back_to_groups(callback: CallbackQuery,state: FSMContext):
    data = await state.get_data()
    level_id = data["level_id"]
    groups = db.get_groups(level_id=level_id)
    await state.set_state(st.MainStates.choosing_grammar_topic)
    await callback.answer()
    await callback.message.edit_text("Что хочешь потренировать?", reply_markup=kb.blitz_groups_keyboard(groups))

#[НАЗАД] в главное меню
@router.callback_query(st.MainStates.choosing_grammar_topic, F.data == "back")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    #await state.clear()
    await callback.answer()

    user_id =  callback.from_user.id
    level = db.get_current_user_level(user_id)
    await callback.message.edit_text("Начинаем тренировку?", reply_markup=kb.main_menu_keyboard(level))

# [ПОЛУЧИТЬ ВОПРОС ДЛЯ ПЕРЕВОДА]  
#@router.callback_query(st.MainState.doing_blitz.answering)
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
    
    if _group_id == 0: _group_id = random.choice(db.get_groups(level_id=_level_id))[0]

    topics = db.get_topics(parent_id=_group_id, level_id=_level_id)

    a = random.choice(db.get_topics(parent_id=_group_id, level_id=_level_id), )[0] 
    
    if _topic_id == 0: _topic_id = a #random.choice(db.get_topics(parent_id=_group_id, level_id=_level_id), )[0] 
    topic_id = a

    _current_question += 1

    if _current_question == 1:
        await message.answer(mes.get_start_bliz_message(_group_id, topic_id ))
        await message.answer("...придумываю предложение...")


    sentence = await cl.get_sentence(user_id=user_id, level_id=_level_id, difficulty=_difficulty, group_id=_group_id, topic_id = topic_id)


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
        #f"<b>Задание  {_current_question} из {_total_question}</b>\n\n"
        f"<b>Задание  {_current_question}</b>\n\n"

        f"<i>{sentence['text']}</i>",
        reply_markup=kb.finish_blitz_keyboard()
)

@router.message(st.MainStates.bliz_answer)
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

    ai_result = await cl.check_answer(
        russian_sentence=current_sentence,
        user_answer=user_answer
    )

    # --------------------------------------------------
    # Сохраняем результат проверки
    # --------------------------------------------------

    questions[current_question]["ai_answer"] = ai_result

    await state.update_data(questions=questions)

    #Идем дальше

    await state.update_data(
        questions=questions
    )

    
    db.save_user_answer(
        user_id=message.from_user.id,
        sentence_id=current_sentence_id,
        user_answer=user_answer,
        ai_answer = json.dumps(
                ai_result,
                ensure_ascii=False
            )
    )

    await message.answer(cl.format_check_result(ai_result))

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
    st.MainStates.bliz_answer,
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

    level = db.get_current_user_level(user_id)

    await message.answer(
        "Начинаем тренировку?",
        reply_markup=kb.main_menu_keyboard(level)
    )
