FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /books_http_proxy/requirements.txt 
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /books_http_proxy/requirements.txt

RUN mkdir /app/data
COPY audiobookshelf /app/audiobookshelf
COPY tg_bot /app/tg_bot
COPY utils /app/utils

COPY *.py /app/

ENTRYPOINT ["python", "books_proxy.py"]
