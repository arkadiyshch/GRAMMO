import os
from pyexpat import model
from unittest import result
from dotenv import load_dotenv
from openai import OpenAI
from openai import AsyncOpenAI
import asyncio
import traceback
import prompts
from prompts import get_check_prompt
import json
import re
import data.database as db


load_dotenv()

openAI_api_key = os.getenv("OPENAI_API_KEY")
ODIROUTER_api_key = os.getenv("ODIROUTER_API_KEY")
BASE_URL = "https://api.odirouter.ai/v1"
#MODEL = "gemini-3.7-flash"
MODEL ="gpt-5.4-mini"
#MODEL="gpt-5.6-terra"
#MODEL="gpt-5.6-sol"
#MODEL="gpt-5.6-luna"
#MODEL="free-gpt-5.6-terra"



from memory import get_user_messages, add_user_message

client = AsyncOpenAI(
    api_key=ODIROUTER_api_key, 
    base_url=BASE_URL, 
    timeout=60.0,
    max_retries=3,)

async def ask_gpt_ODIROUTER(prompt: str, user_id: int) -> str:
    try:
        add_user_message(user_id, "user", prompt)

        messages = get_user_messages(user_id)

        base_instruction ={"role": "system", "content": "Ты дружелюбный телегам бот, который помогает пользователю с грамматикой английского языка. Ты должен давать краткие и понятные объяснения, а также примеры использования."}

        full_message =[base_instruction] + messages

       

        
        response = await client.chat.completions.create(
                model=MODEL,   
                messages=full_message,
                max_tokens=500,
            )


        reply = response.choices[0].message.content
        add_user_message(user_id, "assistant", reply)
        return reply
         

    except Exception as e:    
        traceback.print_exc()
        raise
        


#ODI-ROUTER
async def ask_gpt(prompt: str, user_id: int) -> str:
    try:
        add_user_message(user_id, "user", prompt)

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]

        
        response = await client.chat.completions.create(
                model=MODEL,    
                messages=messages
                #max_tokens=50000,
            )


        reply = response.choices[0].message.content
        add_user_message(user_id, "assistant", reply)
        return reply
         

    except Exception as e:    
        traceback.print_exc()
        raise

async def analize_diagnostic(level: int, answers: list) -> dict:
    answer_text = ""

    for i, item in enumerate(answers, start =1):
        answer_text += (f"\n\nQUESTION {i}\n" f"Russian sentence: {item['question']}\n" f"Student answer: {item['answer']}")

    prompt = prompts.gettestPrompt(level, answer_text)
    response = await ask_gpt(prompt, user_id=0)
    response = re.sub( r"^```json\s*", "", response, flags=re.IGNORECASE ) 
    response = re.sub( r"\s*```$", "", response )

    try:
        result = json.loads(response)
        return result
 
    except json.JSONDecodeError:
        print("Error decoding JSON response:")
        print(response)

        return {
            "overall_score": 0, "estimated_level": "Unknown", "confidence": 0, "answers": [], "strongest_aspects": [], "weakest_aspects": [], "recurring_errors": [], "recommendations": [], "overall_feedback": ( "Не удалось автоматически обработать " "результат диагностики." )
        }



async def main():
    print("Ener text:") 
    text = input()
    result = await ask_gpt_ODIROUTER(text)
    print(result)

def format_diagnostic_result(results: dict) -> str:
    text = ""

    #Общая оценка
    overall_score = results.get("overall_score", 0)
    estimated_level = results.get("estimated_level", "Unknown")
    confidence = results.get("confidence", 0)
    text += ( 
        "<b>Результат диагностики</b>\n\n" 
        f"<b>Предварительный уровень:</b> " f"{estimated_level}\n" 
        f"<b>Средний балл:</b> " f"{overall_score}/10\n" 
        f"<b>Уверенность оценки:</b> " f"{confidence * 100:.0f}%\n" )

    #Анализ ответов
    
    for answer in results.get("answers", []): 
        number = answer.get( "question_number", 0 )
        score = answer.get( "score", 0 ) 
        correct_answer = answer.get( "correct_answer", "" ) 
        feedback = answer.get( "feedback", "" ) 

        text += ( 
            f"\n\n<b>Предложение {number}</b>\n" 
            f"Оценка: <b>{score}/10</b>\n\n" 
            f"<b>Лучший вариант:</b>\n" f"{correct_answer}\n"
              ) 
        #Ошибки

        errors = answer.get( "errors", [] ) 
        if errors: 
            text += "\n<b>Ошибки:</b>\n" 
            for error in errors: 
                category = error.get( "category", "" )
                student_version = error.get( "student_version", "" ) 
                correction = error.get( "correction", "" ) 
                explanation = error.get( "explanation", "" ) 
                text += ( f"\n❌ <b>{category}</b>\n"
                          f"Ваш вариант: " f"<code>{student_version}</code>\n" 
                          f"Лучше: " f"<code>{correction}</code>\n" 
                          f"{explanation}\n" 
                          )
        else: 
            text += ( "\n<b>Ошибок не обнаружено.</b>\n" ) 

        if feedback: text += ( f"\n{feedback}\n" ) 

        #Сильные стороны
        strongest = results.get( "strongest_aspects", [] )
        if strongest:
             text += ( 
                 "\n\n<b>Ваши сильные стороны:</b>\n" ) 
             for item in strongest: 
                 text += f"• {item}\n" 


        #Слабые стороны
        weakest = results.get( "weakest_aspects", [] ) 
        if weakest: 
            text += ( "\n\n<b>Что стоит улучшить:</b>\n" )
            for item in weakest: text += f"• {item}\n" 

        #Потворяющиеся ошибки
        recurring = results.get( "recurring_errors", [] ) 
        if recurring: 
            text += ( "\n\n<b>Повторяющиеся ошибки:</b>\n" ) 
            for error in recurring: 
                category = error.get( "category", "" ) 
                explanation = error.get( "explanation", "" ) 
                text += ( f"\n<b>{category}</b>\n" f"{explanation}\n" ) 
        #Реккомендации
        recommendations = results.get( "recommendations", [] ) 
        if recommendations: 
            text += ( "\n\n<b>Что изучать дальше:</b>\n" ) 
            for recommendation in recommendations: 
                text += ( f"• {recommendation}\n" ) 

        #Общий комментарий
        overall_feedback = results.get( "overall_feedback", "" ) 
        if overall_feedback: 
            text += ( "\n\n<b>Общий комментарий:</b>\n" f"{overall_feedback}" )
    return text


async def generate_sentence(level: str, difficulty: int, group: str, topic:str, previous_sentences=None) -> str:

    prompt = prompts.get_sentence_prompt(
        level=level,
        difficulty=difficulty,
        group = group,
        topic=topic, 
        previous_sentences = previous_sentences
    )

    #print(level)
    #print(difficulty)
    #print(group)
    #print(topic)
    #print(prompt)
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=10000
    )

    sentence = response.choices[0].message.content.strip()
    #sente = save_sentence
    return sentence


async def generate_sentences(prompt: str):

    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=10000
        #reasoning_effort="low"
    )

    sentences = response.choices[0].message.content.strip()
    print(sentences)
    return sentences



async def get_sentence(
    user_id: int,
    level_id: int,
    difficulty: int,
    group_id: int,
    topic_id: int,
    used_sentence_ids: list[int] | None = None
):
   

    # 1. Сначала пытаемся найти готовое предложение в БД
    sentence = db.get_sentence_from_DB(
        user_id=user_id,
        level_id=level_id,
        topic_id=topic_id
    )


    if sentence:
        return {
            "id": sentence[0],
            "text": sentence[1]
        }

    # 2. Если подходящего предложения нет — генерируем новое
    previous_sentences = db.get_last_user_sentences(
            user_id=user_id,
            limit=10
        )
    generated_sentence = await generate_sentence(
        level=db.get_level_name(level_id),
        difficulty=difficulty,
        group =db.get_group_name(group_id),
        topic=db.get_topic_name(topic_id),        
        previous_sentences=previous_sentences
    )

    
        

    # 3. Сохраняем его в БД
    sentence_id = add_sentence(
        sentence=generated_sentence,
        level_id=level_id,
        topic_id=topic_id,
        sentence_type=0
    )

    # 4. Возвращаем предложение
    return {
        "id": sentence_id,
        "text": generated_sentence
    }


async def check_answer(
    russian_sentence: str,
    user_answer: str
):
    print("Начинаем проверку ии")
    prompt = get_check_prompt(
        russian_sentence=russian_sentence,
        user_answer=user_answer
    )

    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Ты строгий но справедливый преподаватель английского языка. Ты проверяешь переводы предлжоений с русского на англйискиц в учебном боте"                    
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )
    print("Ждем ответ от ИИ")
    result = response.choices[0].message.content

    # Преобразуем JSON от ИИ в Python-словарь
    result = json.loads(result)

    return result


async def analyze_training(analysis_data: list) -> dict:

    if not analysis_data:
        return {
            "overall_score": 0,
            "summary": "В этой тренировке пока нет проверенных ответов.",
            "strengths": [],
            "weaknesses": [],
            "what_to_review": [],
            "what_to_practice": [],
            "mastered": [],
            "final_recommendation": ""
        }

    analysis_json = json.dumps(
        analysis_data,
        ensure_ascii=False,
        indent=2
    )

    prompt = prompts.get_training_analysis_prompt(
        analysis_data=analysis_json
    )

    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Ты опытный преподаватель английского языка "
                    "и методист. Анализируй результаты обучения "
                    "объективно и не придумывай ошибки."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    result = response.choices[0].message.content.strip()

    result = re.sub(
        r"^```json\s*",
        "",
        result,
        flags=re.IGNORECASE
    )

    result = re.sub(
        r"\s*```$",
        "",
        result
    )

    try:
        return json.loads(result)

    except json.JSONDecodeError:
        print("Ошибка обработки анализа тренировки:")
        print(result)

        return {
            "overall_score": 0,
            "summary": "Не удалось автоматически проанализировать тренировку.",
            "strengths": [],
            "weaknesses": [],
            "what_to_review": [],
            "what_to_practice": [],
            "mastered": [],
            "final_recommendation": ""
        }



def format_check_result(result: dict) -> str:

    text = "<b>Оценка</b>\n\n"

    text += (
        f"<b>Grammar: "
        f"{result['grammar']['score']}/10</b>\n"
    )

    for error in result["grammar"]["errors"]:
        text += (
            f"❌ {error['wrong']} → "
            f"{error['correct']}\n"
        )

    text += "\n"

    text += (
        f"<b>Vocabulary: "
        f"{result['vocabulary']['score']}/10</b>\n"
    )

    for comment in result["vocabulary"]["comments"]:
        text += f"{comment}\n"

    text += "\n"

    text += (
        f"<b>Accuracy: "
        f"{result['accuracy']['score']}/10</b>\n"
    )

    for comment in result["accuracy"]["comments"]:
        text += f"{comment}\n"

    text += "\n"

    text += (
        f"<b>Spelling: "
        f"{result['spelling']['score']}/10</b>\n"
    )

    for error in result["spelling"]["errors"]:
        text += (
            f"❌ {error['wrong']} → "
            f"{error['correct']}\n"
        )

    # Правильный вариант
    correct_answer = result.get("correct_answer", "")

    if correct_answer:
        text += (
            "\n<b>Правильный вариант:</b>\n"
            f"{correct_answer}\n"
        )

    text += (
        "\n<b>Итог: "
        f"{result['total_score']}/10</b>"
    )

    return text


async def get_difficlty_id(user_id, state):
    data = await state.get_data()
    difficulty_id = data.get("difficulty")
    
    if difficulty_id is None: 
        difficulty_id = db.get_last_difficulty_id_by_user_id(user_id)

    return difficulty_id

    

if __name__ == "__main__":
    asyncio.run(main())

                           

