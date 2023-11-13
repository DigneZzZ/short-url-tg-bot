import os
import sqlite3
import string
import random
import time
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Загружаем переменные окружения
load_dotenv()

# Создаем базу данных
conn = sqlite3.connect('links.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS url(id INTEGER PRIMARY KEY, url TEXT, short_url TEXT, user_id INTEGER, timestamp INTEGER);")
conn.commit()

# Генерируем короткую ссылку
def generate_short_url(length=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

# Обработчик команды start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Отправь мне ссылку, и я сокращу ее для тебя.')

# Обработчик текстовых сообщений
def shorten_url(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    current_time = int(time.time())
    c.execute("SELECT * FROM url WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1", (user_id,))
    last_entry = c.fetchone()
    if last_entry and current_time - last_entry[4] < 10:
        update.message.reply_text('Пожалуйста, подождите 10 секунд перед отправкой следующей ссылки.')
        return
    url = update.message.text
    short_url = generate_short_url()
    c.execute("INSERT INTO url (url, short_url, user_id, timestamp) VALUES (?, ?, ?, ?)", (url, short_url, user_id, current_time))
    conn.commit()
    update.message.reply_text(f'Ваша сокращенная ссылка: {os.getenv("DOMAIN")}/{short_url}')

# Главная функция
def main() -> None:
    updater = Updater(token=os.getenv('TELEGRAM_TOKEN'))

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, shorten_url))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
