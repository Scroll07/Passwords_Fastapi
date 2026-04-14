import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

from src.core.settings import settings as s

bot = Bot(token=s.BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Start command")
    
@dp.message(Command("register"))
async def register_command(message: types.Message):
    await message.answer(f'Твое сообщение: {message.text}')
    
    
    
    



async def main():
    #await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)







