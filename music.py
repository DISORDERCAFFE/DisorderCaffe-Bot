from pytube import YouTube
from youtubesearchpython import VideosSearch
import os
from telegram import Update
from telegram.ext import CallbackContext

async def search_and_send_song(update: Update, context: CallbackContext):
    try:
        query = update.message.text
        await update.message.reply_text("🔍 Ищем песню...")

        search = VideosSearch(query, limit=1)
        results = search.result()

        if not results["result"]:
            await update.message.reply_text("❌ Ничего не найдено!")
            return

        video_url = results["result"][0]["link"]
        yt = YouTube(video_url)
        
        # Фикс для pytube: выбираем поток с аудио
        audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').first()
        
        if not audio_stream:
            await update.message.reply_text("❌ Не удалось извлечь аудио!")
            return

        await update.message.reply_text("⬇️ Скачиваем...")
        out_file = audio_stream.download(filename="song.mp3")
        
        # Переименовываем .mp4 в .mp3 (pytube скачивает как .mp4)
        os.rename(out_file, "song.mp3")
        
        await update.message.reply_audio(audio=open("song.mp3", "rb"))
        os.remove("song.mp3")

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")