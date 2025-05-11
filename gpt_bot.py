import os
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
)
from telegram.error import Conflict, NetworkError, TelegramError
from dotenv import load_dotenv
from music import search_and_send_song
from feedback import send_to_admin
import requests  # Добавлено для работы с DeepSeek API

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")  # Добавлено

# Клавиатура
KEYBOARD = [
    ["📜 Правила", "⚙️ Возможности"],
    ["❓ Задать вопрос", "🎵 Найти песню"],
    ["📩 Написать в Кафешку"]
]

# Класс для работы с Восточными Мудрецами (DeepSeek)
class EasternSages:
    @staticmethod
    async def ask_sages(question: str) -> str:
        """Запрос к Восточным Мудрецам (DeepSeek API)"""
        try:
            headers = {
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": question}],
                "temperature": 0.7
            }
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"⚠️ Мудрецы заняты медитацией, попробуй позже. Ошибка: {str(e)}"

class TelegramBot:
    def __init__(self):
        self.app = None
        self.shutdown_event = asyncio.Event()
        
        # Проверка токенов при инициализации
        if not all([BOT_TOKEN, ADMIN_ID, DEEPSEEK_API_KEY]):
            raise ValueError("Не хватает ключей в настройках!")

    async def start(self, update: Update, context: CallbackContext):
        keyboard = ReplyKeyboardMarkup(KEYBOARD, resize_keyboard=True)
        await update.message.reply_text(
            "🤖 Привет! Я бот от DISORDER CAFFE c музыкой и Восточными Мудрецами. Выбери действие:",
            reply_markup=keyboard
        )

    async def handle_message(self, update: Update, context: CallbackContext):
        text = update.message.text

        if text == "📜 Правила":
            await update.message.reply_text("📌 Правила:\n1. Не вальтуй\n2. Не сноси заборы")

        elif text == "⚙️ Возможности":
            await update.message.reply_text(
                "⚡️ Я умею:\n"
                "- Консультироваться с Восточными Мудрецами\n"
                "- Искать и присылать музыку\n"
                "- Передавать сообщения в Кафешку"
            )

        elif text == "❓ Задать вопрос":
            await update.message.reply_text("Напиши свой вопрос, я загоню его Мудрецам:")
            context.user_data["awaiting_question"] = True

        elif text == "🎵 Найти песню":
            await update.message.reply_text("Введи название песни:")
            context.user_data["awaiting_song"] = True

        elif text == "📩 Написать в Кафешку":
            await update.message.reply_text("Напиши сообщение, я толкну его на Tokyo:")
            context.user_data["awaiting_feedback"] = True

        elif context.user_data.get("awaiting_question"):
            answer = await EasternSages.ask_sages(text)  # Используем новый класс
            await update.message.reply_text(f"🧙‍♂️ Мудрецы ответили:\n\n{answer}")
            context.user_data["awaiting_question"] = False

        elif context.user_data.get("awaiting_song"):
            await search_and_send_song(update, context)
            context.user_data["awaiting_song"] = False

        elif context.user_data.get("awaiting_feedback"):
            await send_to_admin(update, context, ADMIN_ID)
            await update.message.reply_text("✅ Сообщение улетело в Кафешку!")
            context.user_data["awaiting_feedback"] = False

    # ... (остальные методы класса остаются без изменений)

async def main():
    bot = TelegramBot()
    try:
        await bot.run()
    except asyncio.CancelledError:
        await bot.stop()
    except ValueError as e:
        print(f"🔥 Критическая ошибка: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nБот остановлен")
    except ValueError as e:
        print(f"🚨 Ошибка запуска: {e}")