from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dataBase.database import (   
    get_level_name
)

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

#Приветственная клавиатура
def welcome_keyboard():
    
    buttons = [
        [InlineKeyboardButton(text="Да", callback_data="start_blitz")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

#Клавиатура главного меню
def main_menu_keyboard(level=None):
    chengeLevelButtonText = ""        
    if level is None:
        chengeLevelButtonText="Выберите уровень"
    else:
        chengeLevelButtonText=f"Уровень: {get_level_name(level)}"    

    
    buttons = [
        [InlineKeyboardButton(text="Да, начинаем", callback_data="start_blitz")],
        [InlineKeyboardButton(text=chengeLevelButtonText, callback_data="change_level")]
       # [InlineKeyboardButton(text="Правила грамматики", callback_data="1")],
       # [InlineKeyboardButton(text="Политики", callback_data="12")],
       # [InlineKeyboardButton(text="Мои подписки", callback_data="ф1")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def user_level_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="A1", callback_data="level_2"), 
                InlineKeyboardButton(text="A2", callback_data="level_3")
            ],
            [
                InlineKeyboardButton(text="B1",callback_data="level_4"),
                InlineKeyboardButton(text="B2",callback_data="level_5")
            ],
            [
                InlineKeyboardButton(text="C1",callback_data="level_6"),
                InlineKeyboardButton(text="C2",callback_data="level_7")
            ]
        ]
    )


#Выбор группы
def blitz_groups_keyboard(groups):

    # Первая кнопка — отдельной строкой
    buttons = [
        [
            InlineKeyboardButton(
                text="Что угодно",
                callback_data="blitz_group_0"
            )
        ]
    ]

    # Кнопки групп
    group_buttons = []

    for group_id, group_name in groups:
        group_buttons.append(
            InlineKeyboardButton(
                text=group_name,
                callback_data=f"blitz_group_{group_id}"
            )
        )

    # По 3 кнопки в ряд
    n = 2

    for i in range(0, len(group_buttons), n):
        buttons.append(group_buttons[i:i + n])

    # Кнопка "Назад" отдельной строкой
    buttons.append(
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data="back"
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )

#Выбор подтемы
def blitz_topics_keyboard(topics):
    # Первая кнопка — отдельной строкой
        buttons = [
            [
                InlineKeyboardButton(text="Любую", callback_data="blitz_topic_0")
            ]
        ]
    
        # Кнопки групп
        group_buttons = []
    
        for topic_id, topic_name in topics:
            group_buttons.append(InlineKeyboardButton(text=topic_name, callback_data=f"blitz_topic_{topic_id}"))
    
        # Вывод с группировкой в ряд
        n = 2
        for i in range(0, len(group_buttons), n):
            buttons.append(group_buttons[i:i + n])

        
        buttons.append(
            [
                InlineKeyboardButton(text="Назад", callback_data="back")
            ]

        )
        return InlineKeyboardMarkup(inline_keyboard=buttons)

#Завершить тестирование
def finish_blitz_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Пропустить", callback_data="skip_question")],
            [InlineKeyboardButton(text="Завершить тестирование", callback_data="finish_blitz")]
        ]
    )