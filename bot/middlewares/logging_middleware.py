from aiogram import Dispatcher
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Update

class LoggingMiddleware(BaseMiddleware):
    async def on_pre_process_update(self, update: Update, data: dict):
        print(f"Получен апдейт: {update}")

def register_middleware(dp: Dispatcher):
    dp.middleware.setup(LoggingMiddleware())
