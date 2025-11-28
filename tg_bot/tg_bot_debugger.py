import logging
import os
from telethon import types, functions

logger = logging.getLogger(__name__)


class FakeClient:
    """
    Фиктивный клиент, который имитирует метод 'on' TelegramClient,
    но не регистрирует никаких обработчиков событий.
    Используется, когда Telegram-бот не должен запускаться.
    """

    def on(self, *args, **kwargs):
        """
        Возвращает "пустой" декоратор, который просто возвращает исходную функцию.
        """

        def decorator(func):
            return func

        return decorator


async def get_user_info(client, user_or_id):
    if type(user_or_id) == type(1):
        user = await client.get_entity(user_or_id)
    else:
        user = user_or_id

    info = user.first_name
    if user.last_name != None:
        info += f" {user.last_name}"
    if user.phone != None:
        info += f" ({user.phone})"
    return info


async def get_my_id(client, event):
    sender_id = event.sender_id
    user_info = await get_user_info(client, sender_id)
    logging.info(f"command /start from user id {sender_id} ({user_info})")
    await event.respond(f"Your id:\n{sender_id}")


async def set_bot_commands(client):
    common_commands = [
        types.BotCommand(command="start", description="Get my id"),
    ]

    try:

        await client(
            functions.bots.SetBotCommandsRequest(
                scope=types.BotCommandScopeDefault(),
                lang_code="",
                commands=common_commands,
            )
        )

        logger.info("Команды бота успешно установлены.")
    except Exception as e:
        logger.error(f"Ошибка при установке команд: {e}")
