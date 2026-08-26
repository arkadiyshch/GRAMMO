import sqlite3
from datetime import datetime


DB_NAME = "data/GRAMMO.db"



def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def create_tables():
    #print("start_create_tables")
    conn = get_connection()
    cursor = conn.cursor()

    # ============================================================
    # USERS
    # ============================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            user_name TEXT
        )
    """)

    # ============================================================
    # LEVELS
    # ============================================================

    #print("create_levels")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS levels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            sort_order INTEGER NOT NULL
        )
    """)

    # ============================================================
    # USER LEVELS
    # История изменения уровня пользователя
    # ============================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_levels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            user_level TEXT,
            estimated_level TEXT,
            source TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id)
                REFERENCES users(user_id)
        )
    """)

    # ============================================================
    # GRAMMAR TOPICS
    # Иерархия грамматических тем
    # ============================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS grammar_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            parent_id INTEGER,
            level_id INTEGER NOT NULL,

            FOREIGN KEY (parent_id)
                REFERENCES grammar_topics(id),

            FOREIGN KEY (level_id)
                REFERENCES levels(id)
        )
    """)

    # ============================================================
    # SENTENCES
    # ============================================================

    cursor.execute("""
       CREATE TABLE IF NOT EXISTS sentences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sentence TEXT NOT NULL,
            level_id INTEGER NOT NULL,
            grammar_topic_id INTEGER,
            lexical_topic_id INTEGER,
            difficulty_id INTEGER NOT NULL,
            type INTEGER NOT NULL DEFAULT 0,

            FOREIGN KEY (level_id)
                REFERENCES levels(id),

            FOREIGN KEY (grammar_topic_id)
                REFERENCES grammar_topics(id),

            FOREIGN KEY (lexical_topic_id)
                REFERENCES lexical_topics(id),

            FOREIGN KEY (difficulty_id)
                REFERENCES difficultу(id)
        )
    """)

    # ============================================================
    # SUBSCRIPTIONS
    # ============================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan TEXT NOT NULL,
            started_at TIMESTAMP NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            payment_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id)
                REFERENCES users(user_id)
        )
    """)

   

    # ============================================================
    # USER ERRORS
    # Ошибки пользователя
    # ============================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_errors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            user_question_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            error_text TEXT,
            correction TEXT,
            explanation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id)
                REFERENCES users(user_id),

            FOREIGN KEY (user_question_id)
                REFERENCES user_questions(id)
        )
    """)

   # ============================================================
      # USER ANSWERS
      # История ответов
      # ============================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            sentence_id INTEGER NOT NULL,
            user_answer TEXT,
            ai_answer TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id)
                REFERENCES users(user_id),

            FOREIGN KEY (sentence_id)
                REFERENCES sentences(id)
        )
            
        """)

    # ============================================================
    #lexical_topics
    # Лексические темы
    # ============================================================
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

    # ============================================================
    #Сложности 
    #
    # ============================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS difficulty (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        )
    """)
    
    # ============================================================
    #Сложности по пользователям
    #
    # ============================================================
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

    # ============================================================
        #Виды подписок
        #
        # ============================================================
    cursor.execute("""
           CREATE TABLE  IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            audience TEXT NOT NULL CHECK (audience IN ('student', 'teacher'))
        )
        """)

    # ============================================================
    # СОХРАНЯЕМ
    # ============================================================

    conn.commit()
    conn.close()

def add_user(telegram_id: int, username: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM users
        WHERE user_id = ?
        """,
        (telegram_id,)
    )


    user = cursor.fetchone()

    print(user)

    if user is not None:
        conn.close()
        return False

    cursor.execute(
        """
        INSERT INTO users (
            user_id,
            user_name
        )
        VALUES (?, ?)
        """,
        (
            telegram_id,
            username
        )
    )

    conn.commit()
    conn.close()

    return True

def get_diagnostic_questions(level: int, limit: int = 5):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, sentence FROM sentences 
        WHERE level = ?
        and topic = "base" and type = 0 
        ORDER BY RANDOM()
        limit ?              

    ''', (level, limit))
    questions = cursor.fetchall()
    conn.close()

    #print("Reply form DB")
    #print(questions)
    return questions

def seed_levels():
    conn = get_connection()
    cursor = conn.cursor()

    levels = [
        ("A1", 1),
        ("A2", 2),
        ("B1", 3),
        ("B2", 4),
        ("C1", 5),
        ("C2", 6),
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO levels (code, sort_order)
        VALUES (?, ?)
    """, levels)

    conn.commit()
    conn.close()

    print("Уровни добавлены.")

def seed_grammar_topics():
    conn = get_connection()
    cursor = conn.cursor()

    # ============================================================
    # ГРУППЫ ТЕМ
    # ============================================================

    groups = [
        "Времена",
        "Условные предложения",
        "Модальные глаголы",
        "Артикли",
        "Местоимения",
        "Предлоги",
        "Степени сравнения",
        "Пассивный залог",
        "Инфинитив и герундий",
        "Порядок слов",
    ]

    # Сохраняем группы и запоминаем их ID
    group_ids = {}

    for group_name in groups:

        cursor.execute("""
            SELECT id
            FROM grammar_topics
            WHERE name = ?
              AND parent_id IS NULL
        """, (group_name,))

        row = cursor.fetchone()

        if row:
            group_id = row[0]
        else:
            cursor.execute("""
                INSERT INTO grammar_topics (name, parent_id)
                VALUES (?, NULL)
            """, (group_name,))

            group_id = cursor.lastrowid

        group_ids[group_name] = group_id

    # ============================================================
    # ПОДТЕМЫ
    # ============================================================

    topics = {
        "Времена": [
            "Present Simple",
            "Present Continuous",
            "Past Simple",
            "Past Continuous",
            "Future Simple",
            "Present Perfect",
            "Present Perfect Continuous",
            "Past Perfect",
            "Past Perfect Continuous",
            "Future Continuous",
            "Future Perfect",
        ],

        "Условные предложения": [
            "Zero Conditional",
            "First Conditional",
            "Second Conditional",
            "Third Conditional",
        ],

        "Модальные глаголы": [
            "Can / Could",
            "Must / Have to",
            "Should",
            "May / Might",
            "Need",
        ],

        "Артикли": [
            "A / An",
            "The",
            "Zero Article",
        ],

        "Местоимения": [
            "Personal Pronouns",
            "Possessive Pronouns",
            "Object Pronouns",
            "Reflexive Pronouns",
            "Demonstrative Pronouns",
        ],

        "Предлоги": [
            "Prepositions of Time",
            "Prepositions of Place",
            "Prepositions of Movement",
        ],

        "Степени сравнения": [
            "Comparative",
            "Superlative",
        ],

        "Пассивный залог": [
            "Present Simple Passive",
            "Past Simple Passive",
            "Future Simple Passive",
            "Present Perfect Passive",
        ],

        "Инфинитив и герундий": [
            "Infinitive",
            "Gerund",
            "Verb + Infinitive",
            "Verb + Gerund",
        ],

        "Порядок слов": [
            "Basic Word Order",
            "Questions",
            "Negative Sentences",
            "Adverbs Position",
        ],
    }

    # ============================================================
    # СОХРАНЯЕМ ПОДТЕМЫ
    # ============================================================

    for group_name, topic_names in topics.items():

        parent_id = group_ids[group_name]

        for topic_name in topic_names:

            cursor.execute("""
                SELECT id
                FROM grammar_topics
                WHERE name = ?
                  AND parent_id = ?
            """, (topic_name, parent_id))

            exists = cursor.fetchone()

            if not exists:
                cursor.execute("""
                    INSERT INTO grammar_topics (name, parent_id)
                    VALUES (?, ?)
                """, (topic_name, parent_id))

    conn.commit()
    conn.close()

    print("Грамматические темы добавлены.")



#Получаем список грамматических тем
def get_grammar_topics(parent_id:int | None, level_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    print(parent_id)
    if parent_id is None:
        query = """
                SELECT id, name
                FROM grammar_topics
                WHERE parent_id is NULL and level_id = ?
                """
        params = (level_id,) 
        cursor.execute(query, params)
    else:    
        query = """
            SELECT id, name
            FROM grammar_topics
            WHERE parent_id = ? and level_id = ?
        """
        params = (parent_id, level_id,)   
        cursor.execute(query, params)

    print(query)
    topics = cursor.fetchall()
    print(topics)
    conn.close()
    return topics



#Получаем список лексических тем
def get_lexical_topics(parent_id:int | None, level_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    print(parent_id)
    if parent_id is None or parent_id==0:
        query = """
                SELECT id, name
                FROM lexical_topics
                WHERE parent_id is NULL and level_from <= ?
                """
        params = (level_id,) 
        cursor.execute(query, params)
    else:    
        query = """
            SELECT id, name
            FROM lexical_topics
            WHERE parent_id = ? and level_from <= ?
        """
        params = (parent_id, level_id,)   
        cursor.execute(query, params)

    print(query)
    topics = cursor.fetchall()
    print(topics)
    conn.close()
    return topics

#Получаем список тем
def get_parent_grammar_topic_id(topic_id: int):
    print(f"topic_id запрос к бд:{topic_id}")
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT parent_id
    FROM grammar_topics
    WHERE id = ?
    """
    params = (topic_id,)  
    cursor.execute(query, params)
    topics = cursor.fetchall()[0][0]
    conn.close()
    return topics

#Получаем список тем
def get_parent_lexical_topic_id(topic_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT parent_id
    FROM lexical_topics
    WHERE id = ?
    """
    params = (topic_id,)  
    cursor.execute(query, params)
    topics = cursor.fetchall()[0][0]
    conn.close()
    return topics





def get_topics_count(parent_id, level_id: int) -> int:
    conn = get_connection()
    cursor = conn.cursor()
  
    query = """
        SELECT count(id)
        FROM grammar_topics
        WHERE parent_id = ? and level_id = ?
    """
    params = (parent_id, level_id,)  
    cursor.execute(query, params)

    topics_count = cursor.fetchall()[0][0]
    

    conn.close()
    return topics_count




def get_unused_sentence(
    user_id: int,
    level: int,
    topic_id: int | None = None
):
    conn = get_connection()
    cursor = conn.cursor()

    if topic_id is None:
        cursor.execute("""
            SELECT s.id, s.sentence
            FROM sentences s
            WHERE s.level = ?
              AND NOT EXISTS (
                  SELECT 1
                  FROM user_question_history h
                  WHERE h.user_id = ?
                    AND h.sentence_id = s.id
              )
            ORDER BY RANDOM()
            LIMIT 1
        """, (level, user_id))

    else:
        cursor.execute("""
            SELECT s.id, s.sentence
            FROM sentences s
            WHERE s.level = ?
              AND s.topic_id = ?
              AND NOT EXISTS (
                  SELECT 1
                  FROM user_question_history h
                  WHERE h.user_id = ?
                    AND h.sentence_id = s.id
              )
            ORDER BY RANDOM()
            LIMIT 1
        """, (level, topic_id, user_id))

    result = cursor.fetchone()

    conn.close()

    return result
def save_sentence(
    sentence: str,
    level_id: int,
    grammar_topic_id: int | None,
    lexical_topic_id: int | None,
    difficulty_id: int,
    sentence_type: int = 0
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sentences (
            sentence,
            level_id,
            grammar_topic_id,
            lexical_topic_id,
            difficulty_id,
            type
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        sentence,
        level_id,
        grammar_topic_id,
        lexical_topic_id,
        difficulty_id,
        sentence_type
    ))

    sentence_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return sentence_id


def get_blitz_sentence(
    user_id: int,
    level: int,
    topic_id: int | None = None
):
    sentence = get_unused_sentence(
        user_id=user_id,
        level=level,
        topic_id=topic_id
    )

    return sentence

def get_grammar_topic(topic_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, parent_id
        FROM grammar_topics
        WHERE id = ?
    """, (topic_id,))

    topic = cursor.fetchone()

    conn.close()

    return topic


def get_random_grammar_topic():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name
        FROM grammar_topics
        WHERE parent_id IS NOT NULL
        ORDER BY RANDOM()
        LIMIT 1
    """)

    topic = cursor.fetchone()

    conn.close()

    return topic

def add_sentence(sentence: str, level_id: int, topic_id: int, type: int = 0):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sentences (sentence, level_id, topic_id, type)
        VALUES (?, ?, ?, ?)
    """, (sentence, level_id, topic_id, type))

    conn.commit()

    sentence_id = cursor.lastrowid

    conn.close()

    return sentence_id


def get_sentence_from_DB(
    user_id: int,
    level_id: int,
    topic_id: int
):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT id, sentence
            FROM sentences
            WHERE level = ?
            AND topic_id = ?
            AND NOT EXISTS (
                SELECT 1
                FROM user_answers ua
                WHERE ua.user_id = ?
                    AND ua.sentence_id = sentences.id
            )
            ORDER BY RANDOM()
            LIMIT 1
        """

   
    params = (
        level_id,
        topic_id,
        user_id
    )

    cursor.execute(query, params)

    result = cursor.fetchone()
    print(query)
    print(params)

    conn.close()

    return result

def add_user_question(user_id: int, sentence_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO user_questions (user_id, sentence_id)
        VALUES (?, ?)
    """, (user_id, sentence_id))

    conn.commit()
    conn.close()

def get_used_sentence_ids(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT sentence_id
        FROM user_questions
        WHERE user_id = ?
    """, (user_id,))

    result = cursor.fetchall()

    conn.close()

    return [row[0] for row in result]



 
def add_sentence(
    sentence: str,
    level_id: int,
    topic_id: int,
    sentence_type: int = 0
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sentences (
            sentence,
            level,
            topic_id,
            type
        )
        VALUES (?, ?, ?, ?)
    """, (
        sentence,
        level_id,
        topic_id,
        sentence_type
    ))

    sentence_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return sentence_id

def get_current_user_level(user_id: int) -> int | None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_level
        FROM user_levels
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 1
    """, (user_id,))

    result = cursor.fetchone()

    conn.close()

    if result is None:
        return None

    return int(result[0])

def get_current_user_level_id(user_id: int) -> int | None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_level
        FROM user_levels
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 1
    """, (user_id,))

    result = cursor.fetchone()

    conn.close()

    if result is None:
        return None

    return int(result[0])


def save_user_level(
    user_id: int,
    level_id: int,
    estimated_level: str | None = None
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO user_levels (
            user_id,
            user_level,
            estimated_level,
            source,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        level_id,
        estimated_level,
        "user",
        datetime.now()
    ))

    conn.commit()
    conn.close()


def get_level_name(level_id):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT code
        FROM levels
        WHERE id = ?          
    """
    params = (level_id,)
    cursor.execute(query, params)
    result = cursor.fetchone()
    conn.close()
    return result[0]

def get_grammar_group_name(group_id):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT name
        FROM grammar_topics
        WHERE id = ?       
    """
    params = (group_id,)
    cursor.execute(query, params)
    result = cursor.fetchone()
    conn.close()
    return result[0]

def get_grammar_topic_name(topic_id):
    if topic_id is None:
        return "Любая грамматическая тема текущего уровня"
    else:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT name
            FROM grammar_topics
            WHERE id = ?       
        """
        
        params = (topic_id,)
        cursor.execute(query, params)
        result = cursor.fetchone()
        print(result)
        conn.close()
        return result[0]

def get_lexical_topic_name(topic_id):
    if topic_id is None:
        return "Любая тема "
    else:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT name
            FROM lexical_topics
            WHERE id = ?       
        """
        
        params = (topic_id,)
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.close()
        return result[0]

def get_lexical_group_name(group_id):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT name
        FROM lexical_topics
        WHERE id = ?       
    """
    params = (group_id,)
    cursor.execute(query, params)
    result = cursor.fetchone()
    conn.close()
    return result[0]

def get_lexical_topic_name(topic_id):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT name
        FROM lexical_topics
        WHERE id = ?       
    """
    
    params = (topic_id,)
    cursor.execute(query, params)
    result = cursor.fetchone()
    print(result)
    conn.close()
    return result[0]

def get_difficulty_id_by_user_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT difficulty_id
        FROM user_difficulty
        WHERE user_id = ?       
    """
    params = (user_id, )
    cursor.execute(query, params )
    result = cursor.fetchone()

    difficulty=0
    if result is None:
        base_difficulty = 2
        save_user_difficulty(user_id, base_difficulty)
        difficulty = base_difficulty
    else:

        difficulty = result[0]

    
    
    conn.close()

 
    return difficulty


def get_last_difficulty_id_by_user_id(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    print(f"User_id: {user_id}")
    query = """
        SELECT difficulty_id
        FROM user_difficulty
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 1
    """
    params = (user_id, )
    cursor.execute(query, params)
    result = cursor.fetchone()
    difficulty_id = result[0]
    
    conn.close()

 
    return difficulty_id


def get_difficulty_name_by_id(difficulty_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT name
        FROM difficulty
        WHERE id = ?        
    """
    params = (difficulty_id, )
    cursor.execute(query, params)
    result = cursor.fetchone()
    difficulty_name = result[0]
    
    conn.close()

 
    return difficulty_name


def save_user_difficulty(user_id: int, difficulty_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    print(f"difficulty_id {difficulty_id}")

    query = """
        INSERT INTO user_difficulty (
            user_id,
            difficulty_id,
            created_at
        )
        VALUES (?, ?, ?)
    """
    params = (user_id, difficulty_id,  datetime.now(), )
    cursor.execute(query, params )
    
    conn.commit()
    conn.close()


def save_user_answer(
    user_id,
    sentence_id,
    user_answer,
    ai_answer=None
):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO user_answers (
            user_id,
            sentence_id,
            user_answer,
            ai_answer
        )
        VALUES (?, ?, ?, ?)
    """

    cursor.execute(
        query,
        (
            user_id,
            sentence_id,
            user_answer,
            ai_answer
        )
    )

    conn.commit()
    conn.close()

def get_last_user_sentences(


        
    user_id: int,
    limit: int = 10
):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT s.sentence
        FROM user_answers ua
        JOIN sentences s
            ON s.id = ua.sentence_id
        WHERE ua.user_id = ?
        ORDER BY ua.created_at DESC
        LIMIT ?
    """

    cursor.execute(query, (user_id, limit))

    result = cursor.fetchall()

    conn.close()

    return [row[0] for row in result]


#Получаем список тем
def get_difficulties():
    conn = get_connection()
    cursor = conn.cursor()

  
    query = """
        SELECT id, name
        FROM difficulty
        """
    cursor.execute(query)
   
    difficulties = cursor.fetchall()
    conn.close()
    return difficulties