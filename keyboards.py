from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import data.database as db

def diagnostic_level_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="A0", callback_data="diagnostic_level_0")],
        [InlineKeyboardButton(text="A1", callback_data="diagnostic_level_1")],
        [InlineKeyboardButton(text="A2", callback_data="diagnostic_level_2")],
        [InlineKeyboardButton(text="B1", callback_data="diagnostic_level_3")],
        [InlineKeyboardButton(text="B2", callback_data="diagnostic_level_4")],
        [InlineKeyboardButton(text="C1", callback_data="diagnostic_level_5")],
        [InlineKeyboardButton(text="C2", callback_data="diagnostic_level_6")]
    ])
    return keyboard

def blitz_groups_keyboard(groups):
    buttons = []

    # Свободная тема
    buttons.append([
        InlineKeyboardButton(
            text="Свободная тема",
            callback_data="blitz_topic_random"
        )
    ])

    # Группы грамматики
    for group_id, group_name in groups:
        buttons.append([
            InlineKeyboardButton(
                text=group_name,
                callback_data=f"blitz_group_{group_id}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def blitz_specific_topics_keyboard(topics):
    buttons = []

    for topic_id, topic_name in topics:
        buttons.append([
            InlineKeyboardButton(
                text=topic_name,
                callback_data=f"blitz_topic_{topic_id}"
            )
        ])

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )


############################3

#Welcome клавиатура
def welcome_keyboard():
    
    buttons = [
        [InlineKeyboardButton(text="Да", callback_data="welcom_change_level")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

#Клавиатура главного меню
async def main_menu_keyboard(user_id):
   
    level_id = db.get_current_user_level_id(user_id)
    subscription = db.get_user_subscription(user_id)

    if subscription is None:
        subscription_name = "Бесплатная"
    else:
        subscription_name = subscription[2] 
    

    chengeLevelButtonText = ""        
    if level_id is None:
        chengeLevelButtonText="Выберите уровень"
    else:
        chengeLevelButtonText=f"Уровень: {db.get_level_name(level_id)}"    

    
    buttons = [
        [InlineKeyboardButton(text="Тренировка", callback_data="main_training")],
        [InlineKeyboardButton(text=chengeLevelButtonText, callback_data="main_change_level")],
        [InlineKeyboardButton(text=f"Подписка: {subscription_name}", callback_data="user_subscription")],
       # [InlineKeyboardButton(text="Политики", callback_data="12")],
       # [InlineKeyboardButton(text="Мои подписки", callback_data="ф1")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def user_level_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="A1", callback_data="level_id_2"), 
                InlineKeyboardButton(text="A2", callback_data="level_id_3")
            ],
            [
                InlineKeyboardButton(text="B1",callback_data="level_id_4"),
                InlineKeyboardButton(text="B2",callback_data="level_id_5")
            ],
            [
                InlineKeyboardButton(text="C1",callback_data="level_id_6"),
                InlineKeyboardButton(text="C2",callback_data="level_id_7")
            ]
        ]
    )


#Выбор группы
def blitz_groups_keyboard(groups, welcome_mode):

    # Первая кнопка — отдельной строкой
    buttons = [[InlineKeyboardButton(text="Что угодно", callback_data="grammar_group_id_0")]]

    # Кнопки групп
    group_buttons = []

    for group_id, group_name in groups:
        group_buttons.append(InlineKeyboardButton(text=group_name, callback_data=f"grammar_group_id_{group_id}")        )

    n = 2 # Кнопок в ряд
    for i in range(0, len(group_buttons), n):
        buttons.append(group_buttons[i:i + n])

    # Кнопка "Назад" отдельной строкой
    if not welcome_mode:
        buttons.append([InlineKeyboardButton(text="Назад",callback_data="grammar_group_-1")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


#Выбор Меню тренироки 
def trainig_keyboard(level_id: int, grammar_topic_id:int, lexical_topic_id:int, user_id: int ):

    difficylty_id = db.get_last_difficulty_id_by_user_id(user_id)
    difficultyu_name = db.get_difficulty_name_by_id(difficylty_id)

    grammar_topic_name = ""
    if grammar_topic_id is None:
        grammar_topic_name = "Любая"
    else:
        if grammar_topic_id ==0 :
                grammar_topic_name = "Любая"
        else:
            grammar_topic_name = db.get_grammar_topic_name(grammar_topic_id)        
    #print(f"grammar_topic_id: {grammar_topic_id}")

    print(f"lexical_topic_id:{lexical_topic_id}")
    lexical_topic_name = ""
    if lexical_topic_id is None:
        lexical_topic_name = "Любая"
    else:
        if lexical_topic_id ==0 :
                lexical_topic_name = "Любая"
        else:
            lexical_topic_name = db.get_lexical_topic_name(lexical_topic_id)        
    #print(f"grammar_topic_id: {grammar_topic_id}")
    
    buttons = [
        [InlineKeyboardButton(text="-->> НАЧАТЬ ТРЕНИРОВКУ <<-- ", callback_data="training_start")],
        [InlineKeyboardButton(text=f"Грамматика: {grammar_topic_name}", callback_data="training_grammar_topic")],
        [InlineKeyboardButton(text=f"Лексика: {lexical_topic_name}", callback_data="training_lexical_topic")],
        [InlineKeyboardButton(text=f"Сложность: {difficultyu_name}", callback_data="training_difficulty")],
        [InlineKeyboardButton(text="Назад", callback_data="training_back_to_main_menu")]      
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


#Выбор грамматической темы
def grammar_topics_keyboard(grammar_topics, show_back_button: bool):
    # Первая кнопка — отдельной строкой
    buttons = [[InlineKeyboardButton(text="Любую", callback_data="grammar_topic_0")]]
    print("im here")
    # Кнопки групп
    group_buttons = []

    for topic_id, topic_name in grammar_topics:
        #group_buttons.append(InlineKeyboardButton(text=topic_name, callback_data=f"grammar_topic_id_{topic_id}"))
        group_buttons.append(InlineKeyboardButton(text="123", callback_data=f"grammar_topic_id_{topic_id}"))

    # Вывод с группировкой в ряд
    n =1 # По n в ряд
    for i in range(0, len(group_buttons), n):
        buttons.append(group_buttons[i:i + n])

    if show_back_button: buttons.append([InlineKeyboardButton(text="Назад", callback_data="grammar_topic_id_-1")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


 #Выбор грамматической темы
def grammar_topics_keyboard_new(grammar_topics, show_back_button: bool):
    # Первая кнопка — отдельной строкой
    
    print("im here")
    buttons = [[InlineKeyboardButton(text="Любую", callback_data="grammar_topic_0")]]


    for topic_id, topic_name in grammar_topics:
        buttons.append([InlineKeyboardButton(text=topic_name, callback_data=f"grammar_topic_id_{topic_id}")])


    if show_back_button: buttons.append([InlineKeyboardButton(text="Назад", callback_data="grammar_topic_id_-1")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)   

#Выбор лексической темы
def lexical_topics_keyboard(lexical_topics, show_back_button: bool):
    # Первая кнопка — отдельной строкой
    buttons = [[InlineKeyboardButton(text="Любую", callback_data="lexical_topic_id_0")]]

    # Кнопки групп
    group_buttons = []

    for topic_id, topic_name in lexical_topics:
        group_buttons.append(InlineKeyboardButton(text=topic_name, callback_data=f"lexical_topic_id_{topic_id}"))

    # Вывод с группировкой в ряд
    n = 2 # По n в ряд
    for i in range(0, len(group_buttons), n):
        buttons.append(group_buttons[i:i + n])

    if show_back_button: buttons.append([InlineKeyboardButton(text="Назад", callback_data="lexical_topic_id_-1")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

#Выбор сложности 
def difficulty_keyboard(difficulties):

    buttons=[]
    for difficulty_id, difficulty_name in difficulties:
        buttons.append(InlineKeyboardButton(text=difficulty_name, callback_data=f"difficulty_id_{difficulty_id}"))
    
        # Вывод с группировкой в ряд
    n = 1 # По n в ряд
    group_buttons = []
    for i in range(0, len(buttons), n):
        group_buttons.append(buttons[i:i + n])

    group_buttons.append([InlineKeyboardButton(text="Назад", callback_data="difficulty_id_-1")])

    return InlineKeyboardMarkup(inline_keyboard=group_buttons)


#Завершить тестирование
def finish_blitz_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Пропустить", callback_data="skip_question")],
            [InlineKeyboardButton(text="Завершить тестирование", callback_data="finish_blitz")]
        ]
    )


#Клавиатура, которая выводится пользователю вместе с предложением
def sentence_answer_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Завершить", callback_data="finish_training"),
                InlineKeyboardButton(text="Пропустить", callback_data="next_sentence"),
                InlineKeyboardButton(text="Подсказки", callback_data="answer_tips")
            ]
        ]
    )

#Клавиатура, которая выводится пользователю вместе с анаизом ошибок конкретного предложения
def next_sentence_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Завершить", callback_data="finish_training"),
                InlineKeyboardButton(text="Следующий вопрос", callback_data="next_sentence")                
            ]
        ]
    )

#Клавиатура, которая выводится пользователю вместе с анаизом ошибок конкретного предложения
def yes_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Да, начинаем", callback_data="yes_start")                
            ]
        ]
    )

#Клавиатура, которая выводится пользователю вместе с анлаизом ошибок конкретного предложения
def yes2_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Да, мне все понравилось", callback_data="yes2")                
            ]
        ]
    )


#Клавиатура, которая выводится пользователю вместе с предложением
def finish_training_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Главное меню", callback_data="training_main_menu")                
            ]
        ]
    )

#Клавиатура, которая выводится пользователю вместе с предложением
def onboard_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            
                [InlineKeyboardButton(text="Продолжить бесплатно", callback_data="onboard_free")],
                [InlineKeyboardButton(text="Подключить за 350 р.", callback_data="onboard_pay")]
                               
            
        ]
    )


#Клавиатура, которая выводится пользователю вместе с предложением
def finish_training_keyboard2(button_text):
    if button_text is None: button_text = "Главное меню"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=button_text, callback_data="training_main_menu")                
            ]
        ]
    )



#########################################
#Клавиатуры для подписок
#########################################
#Оформить подписку
def subscription_subscribe_keyboard(subcription):
    if subcription is None:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Оформить за 350 руб.", callback_data="subscribe")],
                [InlineKeyboardButton(text="Назад", callback_data="back")] 
            ])
    else:
        return InlineKeyboardMarkup(
            inline_keyboard=[              
                [InlineKeyboardButton(text="Отлично! Давайте тренироваться.", callback_data="back")] 
            ])
    
    

def subscription_cancel_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Оформить за 350 руб.", callback_data="cancel")],
            [InlineKeyboardButton(text="Назад", callback_data="back")] 
        ]
    )

def payment_keyboard(payment_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Оплатить подписку", url=payment_url)],
            [InlineKeyboardButton(text="Назад", callback_data="back")] 
        ]
    )


def subscription_payment_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Изменить email",
        callback_data="change_email"
    )

    builder.button(
        text="Перейти к оплате",
        callback_data="pay_premium"
    )

    builder.adjust(1)

    return builder.as_markup()