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
from deepseek import ask_deepseek
from feedback import send_to_admin

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# Клавиатура
KEYBOARD = [
    ["📜 Правила", "⚙️ Возможности"],
    ["❓ Задать вопрос", "🎵 Найти песню"],
    ["📩 Написать в Кафешку"]
]

class TelegramBot:
    def __init__(self):
        self.app = None
        self.shutdown_event = asyncio.Event()

    async def start(self, update: Update, context: CallbackContext):
        """Обработчик команды /start"""
        keyboard = ReplyKeyboardMarkup(KEYBOARD, resize_keyboard=True)
        await update.message.reply_text(
            "🤖 Привет! Я бот от DISORDER CAFFE c музыкой и Восточными Мудрецами. Выбери действие:",
            reply_markup=keyboard
        )

    async def handle_message(self, update: Update, context: CallbackContext):
        """Обработка всех текстовых сообщений"""
        text = update.message.text

        if text == "📜 Правила":
            await update.message.reply_text("📌 Правила:\n1. Не вальтуй\n2. Не сноси заборы")

        elif text == "⚙️ Возможности":
            await update.message.reply_text(
                "⚡️ Я умею:\n"
                "- Отвечать на вопросы серез Мудрецов\n"
                "- Искать и присылать музыку\n"
                "- Передавать сообщения в Кафешку"
            )

        elif text == "❓ Задать вопрос":
            await update.message.reply_text("Напиши свой вопрос я загоню его на Восточных Мудрецов:")
            context.user_data["awaiting_question"] = True

        elif text == "🎵 Найти песню":
            await update.message.reply_text("Введи название песни:")
            context.user_data["awaiting_song"] = True

        elif text == "📩 Написать в Кафешку":
            await update.message.reply_text("Напиши сообщение я толкну его на Tokyo:")
            context.user_data["awaiting_feedback"] = True

        elif context.user_data.get("awaiting_question"):
            answer = await ask_deepseek(text)
            await update.message.reply_text(f"🤖 Мудрецы ответили:\n\n{answer}")
            context.user_data["awaiting_question"] = False

        elif context.user_data.get("awaiting_song"):
            await search_and_send_song(update, context)
            context.user_data["awaiting_song"] = False

        elif context.user_data.get("awaiting_feedback"):
            await send_to_admin(update, context, ADMIN_ID)
            await update.message.reply_text("✅ Сообщение отправлено!")
            context.user_data["awaiting_feedback"] = False

    async def run(self):
        """Основной цикл работы бота"""
        while not self.shutdown_event.is_set():
            try:
                # Инициализация бота
                self.app = Application.builder().token(BOT_TOKEN).build()
                
                # Регистрация обработчиков
                self.app.add_handler(CommandHandler("start", self.start))
                self.app.add_handler(
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
                )

                print("🔄 Бот запущен и работает...")
                await self.app.run_polling(drop_pending_updates=True)

            except (Conflict, NetworkError) as e:
                print(f"⚠️ Ошибка подключения: {e}. Перезапуск через 5 секунд...")
                await self.safe_shutdown()
                await asyncio.sleep(5)

            except TelegramError as e:
                print(f"🚨 Ошибка Telegram: {e}. Перезапуск через 10 секунд...")
                await self.safe_shutdown()
                await asyncio.sleep(10)

            except Exception as e:
                print(f"💥 Неожиданная ошибка: {e}. Перезапуск через 15 секунд...")
                await self.safe_shutdown()
                await asyncio.sleep(15)

    async def safe_shutdown(self):
        """Безопасное завершение работы"""
        if self.app:
            try:
                await self.app.shutdown()
                await self.app.updater.stop()
            except:
                pass
            finally:
                self.app = None

    async def stop(self):
        """Остановка бота"""
        self.shutdown_event.set()
        await self.safe_shutdown()

async def main():
    bot = TelegramBot()
    try:
        await bot.run()
    except asyncio.CancelledError:
        await bot.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nБот остановлен")