import os
import aiohttp
from pydantic import BaseModel
import base64
from fastapi import Response


class TelegramMessage(BaseModel):
    token: str
    chat_id: int
    message: str


def split_message(text: str, max_length: int = 4096) -> list[str]:
    """Разбивает текст на части, не превышая max_length и не разрывая строки."""
    # Если текст пустой, возвращаем пустой список
    if not text:
        return []

    lines = text.splitlines(keepends=True)
    chunks = []
    current_chunk = ""

    for line in lines:
        # Если одна строка длиннее лимита, жестко режем ее
        if len(line) > max_length:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""

            # Режем длинную строку на куски
            long_line = line
            while len(long_line) > max_length:
                chunks.append(long_line[:max_length])
                long_line = long_line[max_length:]
            current_chunk = long_line
            continue

        # Если добавление строки превысит лимит, сохраняем текущий кусок
        if len(current_chunk) + len(line) > max_length:
            chunks.append(current_chunk)
            current_chunk = line
        else:
            current_chunk += line

    # Добавляем последний оставшийся кусок
    if current_chunk:
        chunks.append(current_chunk)

    return chunks


async def forward_message_to_telegram(data: TelegramMessage):

    final_message = data.message

    try:
        decoded_bytes = base64.b64decode(data.message, validate=True)
        final_message = decoded_bytes.decode("utf-8")
    except Exception:
        final_message = data.message

    # Разбиваем сообщение на части с учетом лимита Telegram
    message_chunks = split_message(final_message, max_length=4000)

    url = f"https://api.telegram.org/bot{data.token}/sendMessage"

    proxy_host = os.getenv("TELEGRAM_PROXY_HOST")
    proxy_port = os.getenv("TELEGRAM_PROXY_PORT")
    proxy_url = (
        f"http://{proxy_host}:{proxy_port}" if proxy_host and proxy_port else None
    )

    last_response_text = ""

    async with aiohttp.ClientSession() as session:
        for chunk in message_chunks:
            payload = {"chat_id": data.chat_id, "text": chunk}

            async with session.post(url, data=payload, proxy=proxy_url) as response:
                response.raise_for_status()
                last_response_text = await response.text()

    # Возвращаем результат последней отправки для совместимости с FastAPI Response
    return Response(content=last_response_text, media_type="application/json")
