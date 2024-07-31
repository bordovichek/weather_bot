from aiogram import Bot, Dispatcher, types
from weather_in_city import weather
import asyncio
import logging
import os

# получаем бот-токкен
with open(os.path.join("C:/Users/slava/PycharmProjects", "310724.txt"), 'r') as bt:
    BOT_TOKKEN = bt.read().strip()

# "создаем" ,jnf
weather_bot = Bot(BOT_TOKKEN)
bot_dsp = Dispatcher()


@bot_dsp.message() #отвечает на сообщение, которое представляет из себя название города
async def find_weather(message: types.Message):
    await message.answer(text="Пару секунд, сейчас все найду")
    await message.answer(text=weather(message.text))


async def main():
    logging.basicConfig(level=logging.INFO) # просто логгирование с уровня INFO
    await bot_dsp.start_polling(weather_bot) # получаем обновления бота


if __name__ == '__main__':
    asyncio.run(main())
