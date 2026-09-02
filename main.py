import asyncio
import logging
from data.database import create_tables

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramAPIError
from middleware.admin_only import AdminOnlyMiddleware
from middleware.rate_limit import RateLimitMiddleware
from dotenv import load_dotenv
import os

from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp_socks import ProxyConnector

from handlers import menu, routes_base_function, training, subscription

from data.database import create_tables
from web import app
import uvicorn
from bot_instance import bot


load_dotenv()
create_tables()


TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ENV = os.getenv("ENV")

logging.basicConfig(level=logging.INFO)


async def mainLocal() -> None:
    #Раскомментировать
    session = AiohttpSession(proxy="socks5://127.0.0.1:3067")
    create_tables()


    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode = ParseMode.HTML),  
        #Раскомментировать
        session=session       
    )

    dp = Dispatcher(storage=MemoryStorage())
    dp.message.middleware(RateLimitMiddleware())
    #dp.message.middleware(AdminOnlyMiddleware())
    dp.include_router(routes_base_function.router)
    dp.include_router(menu.router)
    dp.include_router(training.router)
    dp.include_router(subscription.router)
    
    await bot.set_my_commands([])

    web_task = asyncio.create_task(
        start_web_server()
    )

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

    except TelegramAPIError as e:
        logging.error(f"шибка при запуске TelegramAPIError: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        web_task.cancel()
        await bot.session.close()


async def main() -> None:
    #session = AiohttpSession(proxy="socks5://127.0.0.1:3067")
    create_tables()
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode = ParseMode.HTML) 
        #session=session       
    )

    dp = Dispatcher(storage=MemoryStorage())
    dp.message.middleware(RateLimitMiddleware())
    #dp.message.middleware(AdminOnlyMiddleware())
    dp.include_router(routes_base_function.router)
    dp.include_router(menu.router)
    dp.include_router(training.router)
    dp.include_router(subscription.router)
    
    await bot.set_my_commands([])

    web_task = asyncio.create_task(
        start_web_server()
    )

    print("WEB SERVER TASK CREATED")

    try:
        await dp.start_polling(bot)
    except TelegramAPIError as e:
        logging.error(f"шибка при запуске TelegramAPIError: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        web_task.cancel()
        await bot.session.close()
            

#uvicorn.run(app, host="0.0.0.0", port=8000)


async def start_web_server():
    #await uvicorn.run(app, host="0.0.0.0", port=8000)



    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 3000)),
        log_level="info"
    )

    server = uvicorn.Server(config)

    await server.serve()



if __name__ == "__main__":

    ENV = os.getenv("ENV")
    print(ENV)
    if ENV == "local":
        asyncio.run(mainLocal())
    else:   
        asyncio.run(main())
        #asyncio.run(tr.test_parallel_gen_sentences())
