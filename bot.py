
import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message

from config import TELEGRAM_TOKEN, OPENAI_API_KEY
from openai import OpenAI

logging.basicConfig(level=logging.INFO)

openai_client = OpenAI(api_key=OPENAI_API_KEY)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

dialog_memory = {}

SYSTEM_PROMPT = (
    "Ты — мой персональный лайф-ассистент. "
    "Твоя цель — помогать мне в планировании дня, "
    "давать советы по продуктивности, здоровью и мотивации. "
    "Твой тон дружелюбный, но профессиональный. "
    "Если я ставлю задачу, помогай разбивать её на подзадачи по методу SMART."
)

@dp.message(Command("start"))
async def cmd_start(message: Message):
    dialog_memory[message.from_user.id] = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    await message.answer(
        "Привет 👋 Я твой персональный лайф-ассистент.\n"
        "Напиши, с чем хочешь помочь сегодня."
    )

@dp.message(Command("reset"))
async def cmd_reset(message: Message):
    dialog_memory[message.from_user.id] = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    await message.answer("Память очищена 🔄")

@dp.message(F.text)
async def handle_message(message: Message):
    user_id = message.from_user.id

    if user_id not in dialog_memory:
        dialog_memory[user_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    dialog_memory[user_id].append(
        {"role": "user", "content": message.text}
    )

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=dialog_memory[user_id],
            temperature=0.7,
        )

        reply = response.choices[0].message.content

        dialog_memory[user_id].append(
            {"role": "assistant", "content": reply}
        )

        await message.answer(reply)

    except Exception:
        await message.answer("Ошибка. Попробуй позже.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
