
import sqlite3
from datetime import datetime


DB_NAME = "data/GRAMMO.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def create_tables1():
    #print("start_create_tables")
    conn = get_connection()
    cursor = conn.cursor()

  
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lexical_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            parent_id INTEGER,

            access_level INTEGER NOT NULL DEFAULT 0,

            FOREIGN KEY (parent_id)
                REFERENCES lexical_topics(id)
        )
            
        """)

    conn.commit()
    conn.close()

def create_tables2():
    print("start_create_tables")
    conn = get_connection()
    cursor = conn.cursor()

  
    cursor.execute("""
       
            CREATE TABLE IF NOT EXISTS difficulty (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT
            )
        """)
            

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_difficulty (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        difficulty_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (difficulty_id) REFERENCES difficulty(id)
            )
        """)

    conn.commit()
    conn.close()

    print("start_create_tables")

def create_tables4():
    print("start_create_tables")
    conn = get_connection()
    cursor = conn.cursor()
  
    cursor.execute("""
        CREATE TABLE  IF NOT EXISTS lexical_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            parent_id INTEGER,
            level_from INTEGER NOT NULL,
            subscription_id INTEGER NOT NULL DEFAULT 1,

            FOREIGN KEY (parent_id) REFERENCES lexical_topics(id),
            FOREIGN KEY (level_from) REFERENCES levels(id),
            FOREIGN KEY (subscription_id) REFERENCES subscriptions(id)
        )
        """)

    cursor.execute("""
            CREATE TABLE  IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            audience TEXT NOT NULL CHECK (audience IN ('student', 'teacher'))
        )
        """)
   

    conn.commit()
    conn.close()

 

def seed_lexical_topics():
    conn = get_connection()
    cursor = conn.cursor()

    # ---------------------------------------------------------
    # level_from:
    # A1 = 2
    # A2 = 3
    # B1 = 4
    # B2 = 5
    # C1 = 6
    # C2 = 7
    # ---------------------------------------------------------

    topics = {
        "Путешествия": {
            "level_from": 2,
            "children": [
                ("Бронирую отель", 2),
                ("Покупаю билеты", 2),
                ("Планирую поездку", 2),
                ("Заселяюсь в отель", 2),
                ("Решаю проблему в поездке", 3),
                ("Спрашиваю дорогу", 2),
                ("Пользуюсь транспортом", 2),
                ("Общаюсь с местными", 3),
            ]
        },

        "Работа": {
            "level_from": 2,
            "children": [
                ("Ставлю задачи", 2),
                ("Обсуждаю рабочие вопросы", 2),
                ("Провожу встречи", 3),
                ("Объясняю свою позицию", 3),
                ("Прошу о помощи", 2),
                ("Даю обратную связь", 3),
                ("Обсуждаю сроки", 3),
                ("Обсуждаю зарплату", 4),
                ("Ищу работу", 3),
                ("Прохожу собеседование", 3),
            ]
        },

        "Покупки": {
            "level_from": 2,
            "children": [
                ("Выбираю товар", 2),
                ("Сравниваю товары", 2),
                ("Покупаю товар", 2),
                ("Оплачиваю покупку", 2),
                ("Возвращаю товар", 3),
                ("Решаю проблему с заказом", 3),
                ("Делаю заказ онлайн", 2),
            ]
        },

        "Ресторан и еда": {
            "level_from": 2,
            "children": [
                ("Бронирую столик", 2),
                ("Заказываю еду", 2),
                ("Уточняю состав блюда", 2),
                ("Прошу изменить заказ", 3),
                ("Оплачиваю счёт", 2),
                ("Жалуюсь на обслуживание", 3),
            ]
        },

        "Дом": {
            "level_from": 2,
            "children": [
                ("Покупаю мебель", 2),
                ("Заказываю ремонт", 3),
                ("Общаюсь с арендодателем", 3),
                ("Решаю бытовую проблему", 2),
                ("Приглашаю гостей", 2),
                ("Организую переезд", 3),
            ]
        },

        "Здоровье": {
            "level_from": 2,
            "children": [
                ("Записываюсь к врачу", 2),
                ("Описываю симптомы", 2),
                ("Получаю рекомендации", 2),
                ("Покупаю лекарства", 2),
                ("Обсуждаю лечение", 3),
            ]
        },

        "Общение": {
            "level_from": 2,
            "children": [
                ("Знакомлюсь с людьми", 2),
                ("Поддерживаю разговор", 2),
                ("Рассказываю о себе", 2),
                ("Рассказываю о своих планах", 2),
                ("Обсуждаю интересы", 2),
                ("Выражаю мнение", 3),
                ("Соглашаюсь или возражаю", 3),
            ]
        },

        "Финансы": {
            "level_from": 2,
            "children": [
                ("Оплачиваю покупку", 2),
                ("Снимаю деньги", 2),
                ("Перевожу деньги", 2),
                ("Обсуждаю цену", 2),
                ("Разбираюсь с платежом", 3),
                ("Пользуюсь банком", 2),
            ]
        },

        "Технологии": {
            "level_from": 2,
            "children": [
                ("Настраиваю устройство", 2),
                ("Пользуюсь приложением", 2),
                ("Решаю техническую проблему", 3),
                ("Покупаю технику", 2),
                ("Настраиваю аккаунт", 2),
            ]
        },

        "Свободное время": {
            "level_from": 2,
            "children": [
                ("Планирую отдых", 2),
                ("Покупаю билеты на мероприятие", 2),
                ("Приглашаю друзей", 2),
                ("Обсуждаю фильмы и сериалы", 2),
                ("Рассказываю о своих увлечениях", 2),
            ]
        },

        "Социальная жизнь": {
            "level_from": 2,
            "children": [
                ("Приглашаю кого-то", 2),
                ("Договариваюсь о встрече", 2),
                ("Переношу встречу", 2),
                ("Отменяю встречу", 2),
                ("Поздравляю кого-то", 2),
                ("Прошу об одолжении", 2),
            ]
        },
    }


    # ---------------------------------------------------------
    # Сначала создаём родительские темы
    # ---------------------------------------------------------

    for parent_name, parent_data in topics.items():

        parent_id = insert_topic(
            cursor=cursor,
            name=parent_name,
            parent_id=None,
            level_from=parent_data["level_from"]
        )

        # -----------------------------------------------------
        # Затем дочерние темы
        # -----------------------------------------------------

        for child_name, child_level in parent_data["children"]:

            insert_topic(
                cursor = cursor,
                name=child_name,
                parent_id=parent_id,
                level_from=child_level
            )

    conn.commit()
    conn.close()


def insert_topic(cursor, name, parent_id, level_from):
        print(name, "\n", parent_id, "\n", level_from)
        cursor.execute("""
            SELECT id
            FROM lexical_topics
            WHERE name = ?
              AND parent_id IS ?
        """, (name, parent_id))

        result = cursor.fetchone()

        if result:
            return result[0]

    
        cursor.execute("""
            INSERT INTO lexical_topics (
                name,
                parent_id,
                level_from,
                subscription_id
            )
            VALUES (?, ?, ?, ?)
        """, (
            name,
            parent_id,
            level_from,
            1
        ))

        return cursor.lastrowid





def create_tables5():
    print("start_create_tables")
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE sentences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sentence TEXT NOT NULL,
        level_id INTEGER NOT NULL,
        grammar_topic_id INTEGER,
        lexical_topic_id INTEGER,
        difficulty_id INTEGER,
        type INTEGER NOT NULL DEFAULT 0,

        FOREIGN KEY (level_id)
            REFERENCES levels(id),

        FOREIGN KEY (grammar_topic_id)
            REFERENCES grammar_topics(id),

        FOREIGN KEY (lexical_topic_id)
            REFERENCES lexical_topics(id),

        FOREIGN KEY (difficulty_id)
            REFERENCES difficulty(id)
)
        """)

    conn.commit()
    conn.close()

    print("finish_create_tables")






print("start")
create_tables5()





  
