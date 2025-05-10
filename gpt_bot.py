import os
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram.error import Conflict
from dotenv import load_dotenv
from music import search_and_send_song
from deepseek import ask_deepseek
from feedback import send_to_admin

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

KEYBOARD = [
    ["📜 Правила", "⚙️ Возможности"],
    ["❓ Задать вопрос", "🎵 Найти песню"],
    ["📩 Написать в Кафешку"]
]

async def start(update: Update, context: CallbackContext):
    keyboard = ReplyKeyboardMarkup(KEYBOARD, resize_keyboard=True)
    await update.message.reply_text(
        "🤖 Привет! Я бот от DISORDER CAFFE c музыкой и Восточными Мудрецами. Выбери действие:",
        reply_markup=keyboard
    )

async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    user_id = update.message.from_user.id

    if text == "📜 Правила":
        await update.message.reply_text("📌 Правила:\n1. Не вальтуй\n2. Не сноси заборы")

    elif text == "⚙️ Возможности":
        await update.message.reply_text(
            "⚡️ Я умею:\n"
            "- Отвечать на вопросы с Восточными Мудрецами (кнопка ❓)\n"
            "- Искать и присылать музыку (кнопка 🎵)\n"
            "- Передавать сообщения в Кафешку (кнопка 📩)"
        )

    elif text == "❓ Задать вопрос":
        await update.message.reply_text("Напиши свой вопрос, и я загоню его Восточным Мудрецам.")
        context.user_data["awaiting_question"] = True

    elif text == "🎵 Найти песню":
        await update.message.reply_text("Введи название песни или исполнителя:")
        context.user_data["awaiting_song"] = True

    elif text == "📩 Написать в Кафешку":
        await update.message.reply_text("Напиши сообщение, и я толкну его на Tokyo:")
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

async def run_bot():
    """Функция с обработкой конфликтов"""
    while True:
        try:
            app = Application.builder().token(BOT_TOKEN).build()
            app.add_handler(CommandHandler("start", start))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
            
            print("🔄 Бот запущен...")
            await app.run_polling()
            
        except Conflict:
            print("⚠️ Обнаружен конфликт! Перезапуск через 5 секунд...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"🚨 Критическая ошибка: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(run_bot())