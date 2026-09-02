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
import states as st 
from aiogram.fsm.state import State, StatesGroup
import handlers.training as tr
import prompts as p
import handlers.routes_base_function as rbf


router = Router()

#[START]
@router.message(F.text == "/start")
async def welcome_handler(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(st.MainStates.main_menu)
    user_id = message.from_user.id
    user_name = message.from_user.username
    #level = db.get_current_user_level(user_id)
    
    debug_mode = os.getenv("DEBUG_MODE")
    #if debug_mode: db.delete_user_levels(user_id)
        
    
    level_id = db.get_current_user_level_id(user_id)
    await state.update_data(user_id=user_id, level_id = level_id)    
    db.add_user(telegram_id=user_id, username=user_name)    
    active_messages = []   

    

    cur_mes = message
    active_messages.append({
                "message" : cur_mes,
                "author": "bot",
                "type": "start"
            })   
     
      
    if level_id is None:
        await state.update_data(welcome_mode = True) 
        await state.set_state(st.MainStates.choosing_level)
        cur_mes = await message.answer(mes.get_welcome_message(), reply_markup=kb.user_level_keyboard())
        active_messages.append({
            "message" : cur_mes,
            "author": "bot",
            "type": "menu"
        })                
    else:
        await state.update_data(welcome_mode = False) 
        await state.set_state(st.MainStates.main_menu)

        cur_mes = await message.answer("Главное меню", reply_markup=await kb.main_menu_keyboard(user_id))
        active_messages.append({
                    "message" : cur_mes,
                    "author": "bot",
                    "type": "menu"
                })     
    await state.update_data(active_messages=active_messages)
    await rbf.delete_active_messages(state, type = "start")


####################################################
#Main Menu
####################################################
        
#[Изменить уровень]
@router.callback_query(st.MainStates.main_menu, F.data == "main_change_level")
async def main_choosing_level_handler(callback: CallbackQuery, state: FSMContext):
    #choosing_level(callback, state)
    await state.set_state(st.MainStates.choosing_level)
    await callback.message.edit_text("Какой у вас уровень?", reply_markup=kb.user_level_keyboard())
    await state.update_data(next_state = st.MainStates.main_menu) 


####################################################
#Общее для Welcome и Main menu
####################################################

#Выбор конкретного уровня  
@router.callback_query(st.MainStates.choosing_level, F.data.startswith("level_id_"))
async def choosing_level_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    user_id = data["user_id"]    
    level_id = callback.data.replace("level_id","")[-1]
    level_name = db.get_level_name(level_id)
    grammar_topics = db.get_grammar_topics(parent_id=None,  level_id=level_id)
    welcome_mode = data["welcome_mode"] 
    active_messages = data["active_messages"]

    db.save_user_level(user_id=user_id, level_id=level_id)
    await state.update_data(level_id = level_id)

    if welcome_mode:
        grammar_topic_id = random.choice(grammar_topics)[0]
        topic_name = db.get_grammar_topic_name(grammar_topic_id)
        await callback.message.edit_text(f"Отлично!\n\nДля знакомства с GRAMMO я выберу случайную грамматическую тему по вашему уровню и сформирую 3 предложения - от простого к сложному.\n\nВам нужно их перевести и прислать ответ. \n\nПосле каждого ответа я покажу правильный вариант и разберу ошибки.\n\nГотовы?", reply_markup=kb.yes_keyboard())
        
    else:
        await state.set_state(st.MainStates.main_menu)

        await callback.message.edit_text("Начинаем тренировку?", reply_markup=await kb.main_menu_keyboard(user_id))

        state.update_data(active_messages=active_messages)

#Выбор конкретного уровня  
@router.callback_query(st.MainStates.choosing_level, F.data.startswith("yes_start"))
async def yes_start_welcom_training(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await tr.tarining_start(callback, state)

        
#Выбор грамматического топика. 
@router.callback_query(st.MainStates.choosing_grammar_topic)
async def choosing_grammar_topic_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    level_id = data["level_id"] # Нужен для фильтра уровней
    grammar_topic_id = data.get("grammar_topic_id")
    recursion_depth = data.get("recursion_depth")
    welcome_mode = data["welcome_mode"]
    if recursion_depth is None: recursion_depth = 0  #Уровень рекурсии. ЕСли 1, то это первый вызов
    recursion_depth +=1
    exit_state =  data.get("exit_state")
    callback_id = int(callback.data.split("_")[-1])  #Смотрим, что нажато

    show_back_button = True
    if welcome_mode and recursion_depth == 1: show_back_button=False

    #topics = db.get_grammar_topics(parent_id = grammar_topic_id, level_id=level_id)
    #Возврат назад 
    print (f"call back: {callback_id}")
    print (f"recursion_depth: {recursion_depth}")
    print (f"welcome_mode: {welcome_mode}")

    print (f"recursion_depth:{recursion_depth}")
    
    if callback_id == -1: 
        if recursion_depth == 1:
            if welcome_mode:
                await state.set_state(st.MainStates.choosing_level)
                await callback.message.edit_text("Какой у вас уровень?", reply_markup=kb.user_level_keyboard()) 
            else:
                await state.set_state(exit_state) 
                await main_training(callback, state)
        else:
            recursion_depth-=1
            parent_topic_id = db.get_patent_grammar_topic_id(grammar_topic_id)

            if recursion_depth==0:
                await state.update_data(grammar_topic_id = parent_topic_id , recursion_depth = None)
                await state.set_state(exit_state)
            else:
                topics = db.get_grammar_topics(parent_id = grammar_topic_id, level_id=level_id)
                await callback.message.edit_text("Что хочешь потренировать?", reply_markup=kb.grammar_topics_keyboard(topics, show_back_button))
                        

    if callback_id == 0: #Любое значение из списка.
        print(f"Топик выбран: {db.get_grammar_topic_name(grammar_topic_id)}")
        if welcome_mode:
            await state.set_state(st.MainStates.bliz_prepare)     
        else: 
            await state.set_state(exit_state)   
            await main_training(callback, state)  
        return
            

    if callback_id > 0: #Топик выбран
        grammar_topic_id = callback_id
        topics = db.get_grammar_topics(grammar_topic_id, level_id)
        if len(topics)==0:
            print(f"выбрана тема: {db.get_grammar_topic_name(grammar_topic_id)}")
            print(f"welcome mode: {welcome_mode}")
            await state.update_data(grammar_topic_id = grammar_topic_id , recursion_depth = None)
            if welcome_mode:
                await state.set_state(st.MainStates.bliz_prepare)     
            else: 
                await state.set_state(exit_state) 
                await main_training(callback, state)     
        else:
            await state.update_data(grammar_topic_id = grammar_topic_id , recursion_depth = recursion_depth)
            await callback.message.edit_text("Что хочешь потренировать?", reply_markup=kb.grammar_topics_keyboard(topics, True))

      
#Выбор лексического топика. 
@router.callback_query(st.MainStates.choosing_lexical_topic)
async def choosing_lexical_topic_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    level_id = data["level_id"] # Нужен для фильтра уровней
    lexical_topic_id = data.get("lexical_topic_id")
    recursion_depth = data.get("recursion_depth")
    #welcome_mode = data["welcome_mode"]
    if recursion_depth is None: recursion_depth = 0  #Уровень рекурсии. ЕСли 1, то это первый вызов
    recursion_depth +=1
    exit_state =  data.get("exit_state")
    callback_id = int(callback.data.split("_")[-1])  #Смотрим, что нажато
    show_back_button = True

    print("main parametrs")
    print(f"level_id {level_id}")
    print(f"lexical_topic_id {lexical_topic_id}")
    print(f"recursion_depth {recursion_depth}")
    print(f"exit_state {exit_state}")
    print(f"callback_id {callback_id}")
    
    
    if callback_id == -1: 
        if recursion_depth == 1:
            await state.set_state(exit_state) 
            await main_training(callback, state)
        else:
            recursion_depth-=1
            parent_lexical_id = db.get_parent_lexical_topic_id(lexical_topic_id)

            if recursion_depth==0:
                await state.update_data(lexical_topic_id = parent_lexical_id , recursion_depth = None)
                await state.set_state(exit_state)
            else:
                topics = db.get_lexical_topics(parent_id = parent_lexical_id, level_id=level_id)
                await callback.message.edit_text("Выберите тему?", reply_markup=kb.lexical_topics_keyboard(topics, show_back_button))
                        

    if callback_id == 0: #Любое значение из списка.
        print(f"__________recursion_depth________________{lexical_topic_id}")
            
        if recursion_depth > 1:        
            print(f"__________lexical_topic_id________________{lexical_topic_id}")
            parent_lexical_id =lexical_topic_id# db.get_patent_lexical_topic_id(lexical_topic_id)
            print(f"__________parent_lexical_id________________{parent_lexical_id}")
        else:
            parent_lexical_id = 0
        await state.update_data(lexical_topic_id = parent_lexical_id , recursion_depth = None)
        await state.set_state(exit_state)   
        await main_training(callback, state)  

        return
            

    if callback_id > 0: #Топик выбран
        lexical_topic_id = callback_id
        topics = db.get_lexical_topics(parent_id=lexical_topic_id, level_id = level_id)
        if len(topics)==0:
            await state.update_data(lexical_topic_id = lexical_topic_id , recursion_depth = None)
            await state.set_state(exit_state) 
            await main_training(callback, state)  

            return

        else:
            await state.update_data(lexical_topic_id = lexical_topic_id , recursion_depth = recursion_depth)
            await callback.message.edit_text("Выберите тему?", reply_markup=kb.lexical_topics_keyboard(topics, True))
 
        print(f"callback_id {callback_id}")
####################################################
#Trainig menu
####################################################           

#Возврат в главное меню из тренировки
@router.callback_query(st.MainStates.main_menu, F.data == "training_back_to_main_menu")
async def training_back_to_main_menu_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    level_id = data["level_id"] 
    user_id = data["user_id"]  
    await callback.message.edit_text("Главное меню", reply_markup=await kb.main_menu_keyboard(user_id))

# Открываем меню тренировки
@router.callback_query(st.MainStates.main_menu, F.data.startswith("main_training"))
async def main_training_handler(callback: CallbackQuery, state: FSMContext):
    await main_training(callback, state)

async def main_training(callback: CallbackQuery, state: FSMContext):
    print("Main Training")
    await callback.answer()

    data = await state.get_data()

    grammar_topic_id = data.get("grammar_topic_id")
    lexical_topic_id = data.get("lexical_topic_id")
    level_id = data.get("level_id")
    user_id = data["user_id"]
    active_messages = data["active_messages"]

    
    difficulty_id = data.get("difficulty_id")
    if difficulty_id is None:
        difficulty_id = await cl.get_difficlty_id(user_id, state) 
        await state.update_data(difficulty_id = difficulty_id)

        
    if grammar_topic_id is None: grammar_topic_id=0
    if lexical_topic_id is None: lexical_topic_id=0

    await state.set_state(st.MainStates.main_menu)  
    await callback.message.edit_text("Тренировка", 
        reply_markup=kb.trainig_keyboard(level_id=level_id, grammar_topic_id = grammar_topic_id, lexical_topic_id=lexical_topic_id, user_id=user_id))
            

# Что ловим: нажатие кнопки граматического топика в режиме тренировка 
@router.callback_query(st.MainStates.main_menu, F.data.startswith("training_grammar_topic"))
async def main_training_grammar_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    level_id = data["level_id"]
    groups = db.get_grammar_topics(parent_id=None,  level_id=level_id)
    print(level_id)
    print(groups)
    await callback.message.edit_text("Что хочешь потренировать?", reply_markup=kb.blitz_groups_keyboard(groups, False))
    await state.set_state(st.MainStates.choosing_grammar_topic)
    await state.update_data(exit_state = st.MainStates.main_menu)

# Что ловим: нажатие кнопки лексического топика в режиме тренировка 
@router.callback_query(st.MainStates.main_menu, F.data.startswith("training_lexical_topic"))
async def main_training_lexical_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    level_id = data["level_id"]
    groups = db.get_lexical_topics(parent_id=None,  level_id=level_id)

    print(f"level_id {level_id}")
    print(f"lexical_topics {groups}")
    await callback.message.edit_text("Выберите тему", reply_markup=kb.lexical_topics_keyboard(groups, True))
    await state.set_state(st.MainStates.choosing_lexical_topic)
    await state.update_data(exit_state = st.MainStates.main_menu)
    
# Что ловим: нажатие кнопки сложности режиме тренировка 
@router.callback_query(st.MainStates.main_menu, F.data.startswith("training_difficulty"))
async def training_difficulty_handler(callback: CallbackQuery, state: FSMContext):
    print("choose difficulty")
    await callback.answer()
    difficulties = db.get_difficulties()
    await callback.message.edit_text("Что хочешь потренировать?", reply_markup=kb.difficulty_keyboard(difficulties))
    
#Выбор конкретной сложности  
@router.callback_query(st.MainStates.main_menu, F.data.startswith("difficulty_id_"))
async def choosing_difficulty_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    user_id = data["user_id"]    
    callback_id = int(callback.data.split("_")[-1])  #Смотрим, что нажато

    if callback_id ==-1:
        a = True
    else:
        difficulty_id = callback_id
        await state.update_data(next_state = st.MainStates.bliz_prepare, difficulty_id  = difficulty_id) 
        db.save_user_difficulty(user_id, difficulty_id)

    #Возврат в режим тренировки
    await main_training(callback, state)




#Запуск тренировки
@router.callback_query(st.MainStates.main_menu, F.data.startswith("training_start"))
async def main_training_start_handler(callback: CallbackQuery, state: FSMContext):
    print("Im here ready to start training")
    await callback.answer()
    await tr.tarining_start(callback, state)



