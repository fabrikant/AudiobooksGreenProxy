import os
import aiohttp
from pydantic import BaseModel


class TelegramMessage(BaseModel):
    token: str
    chat_id: int
    message: str


async def forward_message_to_telegram(data: TelegramMessage):

    url = f"https://api.telegram.org/bot{data.token}/sendMessage"
    payload = {"chat_id": data.chat_id, "text": data.message}

    proxy_host = os.getenv("TELEGRAM_PROXY_HOST")
    proxy_port = os.getenv("TELEGRAM_PROXY_PORT")

    proxy_url = None

    if proxy_host and proxy_port:
        proxy_url = f"http://{proxy_host}:{proxy_port}"

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, proxy=proxy_url) as response:
            response.raise_for_status()
            return await response.text()
