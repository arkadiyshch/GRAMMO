import dataBase.database as db
def get_welcome_message():
    res = """Привет! Я GRAMO.\nЗакрываю пробелы грамматике короткими тренировками: \n\n ПРЕДЛОЖЕНИЕ -->> ТВОЙ ПЕРЕВОД -->> ПРОВЕРКА \n\n"""
    return res

def get_start_bliz_message(goup_id: int, topic_id: int):
    group_name = db.get_group_name(goup_id)
    topic_name = db.get_topic_name(topic_id)
    res= f"Тренируем тему:\n\n{group_name}\n{topic_name}\n\nПереведи одно за другим следущие 10 предложений на английский язык. \nЕсли сложно - можно пропустить."
    
    return res

