import os
import requests
from dotenv import load_dotenv

load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

async def ask_deepseek(question: str) -> str:
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
        response_data = response.json()
        
        if "choices" not in response_data:
            return "⚠️ Мудрецы пока заняты. Попробуй позже."
        
        return response_data["choices"][0]["message"]["content"]
    
    except Exception as e:
        return f"⚠️ Ошибка: {str(e)}"