from database import pool
import random

LEVELS = {}
GRAMMAR_TOPICS = {}
DIFFICULTIES = {}


##LOAD DATA

def load_reference_data():
    global LEVELS, GRAMMAR_TOPICS, DIFFICULTIES

    with pool.connection() as conn:
        with conn.cursor() as cursor:

            #Levels
            cursor.execute("""
                SELECT *
                FROM levels
            """)
            columns = [desc.name for desc in cursor.description]
            LEVELS.clear()
            for row in cursor.fetchall():
                data = dict(zip(columns, row))
                LEVELS[data["id"]] = data


            #Grammar Topics
            cursor.execute("""
                SELECT *
                FROM grammar_topics
            """)
            
            columns = [desc.name for desc in cursor.description]            
            GRAMMAR_TOPICS.clear()
            for row in cursor.fetchall():
                data = dict(zip(columns, row))
                GRAMMAR_TOPICS[data["id"]] = data
            
            #DIFFICULTIES
            cursor.execute("""
                SELECT *
                FROM difficulty
                ORDER BY id
            """)
            columns = [desc.name for desc in cursor.description]  
            DIFFICULTIES.clear()            
            for row in cursor.fetchall():
                data = dict(zip(columns, row))
                DIFFICULTIES[data["id"]] = data

##LEVELS
def get_level_name(level_id):
    return LEVELS[level_id]["code"]

##GRAMMAR_TOPICS


def get_grammar_topics(parent_id: int | None, level_id: int):
    
    if parent_id is None:
        topics = [
                topic
                for topic in GRAMMAR_TOPICS.values()
                if topic["parent_id"] is None                   
            ]
        topics.sort(key=lambda topic: (topic["name"]))

    else:
        topics = [
                topic
                for topic in GRAMMAR_TOPICS.values()
                if topic["parent_id"] == parent_id      
            ]
        topics.sort(key=lambda topic: (topic["level_id"], topic["name"]))
    
   

    topics2 =  [
        (topic["id"], topic["name"])
        for topic in topics
    ]


    return topics2

def get_random_grammar_topic():
    topics = [
        topic
        for topic in GRAMMAR_TOPICS.values()
        if topic["parent_id"] is not None
    ]

    if not topics:
        return None

    return random.choice(topics)["id"]
     
def get_grammar_topic_name(grammar_topic_id):
    return GRAMMAR_TOPICS[grammar_topic_id]["name"]

def get_parent_grammar_topic_id(grammar_topic_id):
    return GRAMMAR_TOPICS[grammar_topic_id]["parent_id"]


##DIFFICULTIES
def get_difficulties():
    difficulties = [
            difficulty
            for difficulty in DIFFICULTIES.values()                              
        ]
    
    difficulties2 = [
        (difficulty["id"], difficulty["name"])
        for difficulty in difficulties
    ]
        
    return difficulties2
 