import os
import aiohttp
from pydantic import BaseModel
import base64
from fastapi import Response


class TelegramMessage(BaseModel):
    token: str
    chat_id: int
    message: str


async def forward_message_to_telegram(data: TelegramMessage):

    final_message = data.message

    try:
        # validate=True проверяет строку на строгое соответствие алфавиту Base64
        decoded_bytes = base64.b64decode(data.message, validate=True)
        # Если декодирование прошло успешно, пробуем перевести в UTF-8 текст
        final_message = decoded_bytes.decode("utf-8")
    except Exception:
        # Если возникла ошибка (не Base64 или битые байты), оставляем текст как есть
        final_message = data.message

    url = f"https://api.telegram.org/bot{data.token}/sendMessage"
    payload = {"chat_id": data.chat_id, "text": final_message}

    proxy_host = os.getenv("TELEGRAM_PROXY_HOST")
    proxy_port = os.getenv("TELEGRAM_PROXY_PORT")

    proxy_url = None

    if proxy_host and proxy_port:
        proxy_url = f"http://{proxy_host}:{proxy_port}"

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, proxy=proxy_url) as response:
            response.raise_for_status()
            telegram_raw_json = await response.text()
            return Response(content=telegram_raw_json, media_type="application/json")
