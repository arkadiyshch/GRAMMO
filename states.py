from aiogram.fsm.state import State, StatesGroup

class DiagnosticState(StatesGroup):
    choosing_level = State()
    answering = State()


class MainStates(StatesGroup):
    main_menu = State()
  
    choosing_level = State() # Отлавливаем вход
    choosing_grammar_topic = State() # Выбор топика
    choosing_lexical_topic = State() # Выбор топика
    
    

    bliz_prepare = State()
    bliz_ask = State()
    bliz_answer = State()
    bliz_tips = State()

    subscription = State() # Выбор топика

    email = State()
    


#Что храниться в данных state
#Настройки
#user_id
#user_name
#level_id  -> A1 | A2 | B1 | B2 | C1 | C2 -> коды от 2 до 7
#group_id  
#topic_id 
#difficulty = 1 | 2 | 3

# --- прогресс блица ---
#total_questions - всего вопросов
#current_question - текущий вопрос

#Вопросы и ответы
#questions={} вопросы (id, text)
#answers={} ответы
#words {} ответы {слово - перевод}


