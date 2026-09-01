import data.database as db



def get_welcome_message():
    res = """Привет! Я GRAMMO.\nДавай я покажу, как тут все устроено.\nКакой у вас примерный уровень английского?"""
    return res

def get_start_bliz_message(goup_id: int, topic_id: int):
    group_name = db.get_group_name(goup_id)
    topic_name = db.get_topic_name(topic_id)
    res= f"Тренируем :\n{group_name}: {topic_name}\n\nПереведи 10 предложений на англиский язык."
    
    return res


def get_onboard_mes():
    res = """Беслплатно можно тренироваться каждый день 
    Лимит: 3 предложения в день.

    С подпиской за 350 руб./мес вы получите:
     - тренирвки без ограничений
     - выбор грамматических тем
     - выбор лексических тем
     - выбор сложности
     - больше заданий для полноценной тренировки"""
    return res



####################################################
#Подписки
####################################################
#Подписаться
def get_user_subscription_mes(subscriotion):
    res = "-1"
    if subscriotion is None:
        res = """Ваша подписка — Free\n\nС Premium подпиской нет ограничений не объям тренировок и выбор грамматических тем.\n\nСтоимость — 350 ₽ за 1 месяц."""

    elif subscriotion[1] == "premium":
        res = f"""Ваша подписка — premium доступна до {subscriotion[7]}.\n\nУ Вас нет ограничений не объём тренировок и выбор грамматических тем."""
    return res


     
