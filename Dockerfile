FROM python:3.9-slim-buster

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir python-telegram-bot

CMD [ "python", "./bot.py" ]
