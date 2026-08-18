def gettestPrompt(level, answers_text):

    prompt = f""" 
    You are an expert English teacher and CEFR language assessor. 
    You are evaluating a student's English diagnostic test. 
    The student selected approximately CEFR level: {level}. 
    The student translated Russian sentences into English.
     Here are the questions and answers: {answers_text}.
     Analyze ALL answers together. 
     IMPORTANT: 
     1. Do not require the exact reference translation. 
     2. A grammatically correct alternative translation must NOT be considered an error. 
     3. Distinguish between: 
        - actual grammatical errors 
        - vocabulary problems 
        - unnatural but acceptable expressions 
        - stylistic alternatives 
     4. Do not invent errors. 
     5. Consider the student's selected level. 
     6. Identify recurring errors across multiple answers. 
     7. Evaluate the student's actual demonstrated English ability, not only the selected level. 
     
     Analyze the following aspects: 
        - grammar 
        - vocabulary
        - word order 
        - articles 
        - prepositions 
        - verb tenses 
        - subject-verb agreement 
        - plural forms 
        - sentence structure 
        - spelling 
        - meaning preservation 
        - naturalness 
        - lexical choice. 
        
        For every actual error, provide: 
        - the student's version 
        - the corrected version 
        - explanation 
        - error category 
        Then provide: 
        - score from 0 to 10 for each answer 
        - overall score from 0 to 10 
        - estimated CEFR level 
        - confidence from 0 to 1 
        - strongest aspects 
        - weakest aspects 
        - recurring errors 
        - recommendations for further study 

        Prepare reply in Russian language
        Return ONLY valid JSON. 
        
        Use exactly this structure: {{ 
            "overall_score": 0, 
            "estimated_level": "A1", 
            "confidence": 0.0,

            "answers": [ 
                {{ 
                    "question_number": 1, 
                    "score": 0, 
                    "correct_answer": "", 
                    "meaning_preserved": true, 
                    "errors": [
                      {{ 
                        "category": "grammar", 
                        "student_version": "", 
                        "correction": "", 
                        "explanation": "" 
                        }} ], 
                    "feedback": "" 
                }} ], 
                
                "strongest_aspects": [], 
                "weakest_aspects": [], 
                "recurring_errors": [ 
                {{ 
                    "category": "", 
                    "explanation": "", 
                    "examples": [] 
                }} ],
                 
                 "recommendations": [],
                 "overall_feedback": "" 
            }} """

    return prompt

def get_sentence_prompt(level: str, difficulty: int, group: str, topic: str, previous_sentences=None) -> str:



    previous_sentences_str = "\n".join(previous_sentences)

    difficulty_description = {
        0: """
        Предложение должно быть немного проще среднего предложения
        для данного уровня пользователя.

        Используй простую лексику и относительно простую структуру предложения.
        Не опускайся более чем на один уровень CEFR.
        """,

                1: """
        Предложение должно соответствовать обычной сложности
        данного уровня CEFR.

        Используй естественную лексику и грамматическую структуру,
        характерные для этого уровня.
        """,

                2: """
        Предложение должно находиться в верхней части данного уровня CEFR.

        Можно использовать более разнообразную лексику, дополнительные
        обстоятельства, придаточные предложения или более сложную структуру.

        Однако предложение всё ещё должно соответствовать указанному
        уровню CEFR и не должно требовать грамматики существенно более
        высокого уровня.
        """
    }

    difficulty_text = difficulty_description.get(
        difficulty,
        difficulty_description[1]
    )

    return f"""
    Ты создаёшь задание для тренировки английского языка.
    Уровень пользователя: {level}
    Грамматическая тема:
    {group}: {topic} 
    {difficulty_text}
    Задача:

    Сгенерируй ОДНО естественное предложение на русском языке,
    которое пользователь должен будет перевести на английский.

    Критически важно:
    1. Предложение должно проверять именно грамматическую тему:
    
    {group}: {topic} 

    2. Не используй другую грамматическую конструкцию вместо основной
    проверяемой конструкции.

    3. Уровень лексики и общая сложность должны соответствовать уровню
    пользователя: {level}.

    4. Не делай предложение искусственным или похожим на учебниковый шаблон.

    5. Не давай английский перевод.

    6. Не объясняй свой выбор.

    7. Верни только одно русское предложение.

    8. Предлоение не должно быть похоже по смыслу на следующие: 
    {previous_sentences_str}
    
    Пример правильного результата:

    Я встретил своего старого друга возле станции вчера вечером.
    """


def get_check_prompt(russian_sentence: str, user_answer: str) -> str:   
    return  f"""
    Ты проверяешь перевод с русского на английский
    в учебном боте для изучения английского языка.

    Русское предложение:
    {russian_sentence}

    Ответ пользователя:
    {user_answer}

    Проверь ответ по четырём критериям:

    1. Grammar — грамматика
    2. Vocabulary — выбор и употребление слов
    3. Accuracy — насколько точно передан смысл исходного предложения
    4. Spelling — орфография

    Для каждого критерия поставь оценку от 0 до 10.

    ВАЖНЫЕ ПРАВИЛА:

    - Не придирайся к незначительным стилистическим различиям.
    - Не считай ошибкой корректный английский вариант, если он естественно передаёт смысл.
    - Если пользователь использовал грамматически правильную конструкцию, не исправляй её только потому, что существует другой вариант.
    - В Grammar указывай только реальные грамматические ошибки.
    - В Vocabulary указывай ошибки выбора или употребления слов.
    - В Accuracy оценивай соответствие перевода исходному русскому предложению.
    - В Spelling указывай только реальные орфографические ошибки.
    - Не дублируй одну и ту же ошибку во всех категориях.
    - Если ошибок нет, верни пустой список.
    - Комментарии должны быть короткими и понятными пользователю.
    - Не переписывай весь ответ пользователя.
    - Не объясняй очевидные вещи.
    - Не используй Markdown.

    Верни результат СТРОГО в JSON следующего формата:

    {{
    "grammar": {{
        "score": число от 0 до 10,
        "errors": [
        {{
            "wrong": "ошибочный фрагмент",
            "correct": "исправленный вариант"
        }}
        ]
    }},
    "vocabulary": {{
        "score": число от 0 до 10,
        "comments": [
        "краткий комментарий"
        ]
    }},
    "accuracy": {{
        "score": число от 0 до 10,
        "comments": [
        "краткий комментарий"
        ]
    }},
    "spelling": {{
        "score": число от 0 до 10,
        "errors": [
        {{
            "wrong": "ошибочный фрагмент",
            "correct": "исправленный вариант"
        }}
        ]
    }},
    "total_score": число от 0 до 10
    }}
    """