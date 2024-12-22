from aiogram import Router
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any


class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[TelegramObject,
                                                Dict[str, Any]], Any],
                       msg: TelegramObject, data: Dict[str, Any]) -> Any:
        # Логирование или любая другая обработка перед вызовом обработчика
        print(f"Получен объект: {msg}")

        # Вызов следующего обработчика
        return await handler(msg, data)


def register_middleware(router: Router):
    router.message.middleware(LoggingMiddleware())
