import logging
import os

logger = logging.getLogger(__name__)

try:
    TELEGRAM_ADMIN_ID = int(os.getenv("TELEGRAM_ADMIN_ID", ""))
except ValueError:
    logger.info("TELEGRAM_ADMIN_ID environment variable is not a valid integer.")
    TELEGRAM_ADMIN_ID = 0  # Or handle the error as appropriate for your application
except TypeError:
    logger.info(
        "TELEGRAM_ADMIN_ID environment variable is not set or is not a valid integer."
    )
    TELEGRAM_ADMIN_ID = 0  # Or handle the error as appropriate for your application


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
