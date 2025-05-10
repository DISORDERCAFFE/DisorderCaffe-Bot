from telegram import Update
from telegram.ext import CallbackContext
from datetime import datetime

async def send_to_admin(update: Update, context: CallbackContext, admin_id: str):
    user = update.message.from_user
    registration_date = datetime.fromtimestamp(user.id >> 32).strftime("%Y-%m-%d")  # Примерное время регистрации
    
    message = (
        "📩 *Новое сообщение от пользователя:*\n\n"
        f"✍️ *Текст:* `{update.message.text}`\n\n"
        "👤 *Информация об авторе:*\n"
        f"- ID: `{user.id}`\n"
        f"- Username: @{user.username}\n"
        f"- Имя: {user.first_name}\n"
        f"- Фамилия: {user.last_name}\n"
        f"- Язык: {user.language_code}\n"
        f"- Профиль: [тык](tg://user?id={user.id})\n"
        f"- Аккаунт создан: ~{registration_date}\n"
    )
    
    await context.bot.send_message(
        chat_id=admin_id,
        text=message,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )