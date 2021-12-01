from aiogram import executor

from config import admin_id
from database import create_db
from keyboards.default.admin_item import menu
from load_all import bot
from set_bot_commands import set_default_commands

async def on_shutdown(dp):
    await bot.close()


async def on_startup(dp):
    await create_db()
    await set_default_commands(dp)
    await bot.send_message(admin_id, "👋Bot ishga tushdi!👋", reply_markup=menu)


if __name__ == '__main__':
    from admin_panel import dp
    from handlers import dp

    executor.start_polling(dp, on_shutdown=on_shutdown, on_startup=on_startup)
