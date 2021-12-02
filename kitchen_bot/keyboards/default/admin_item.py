from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="↗️Mahsulot_qo`shish↗️"),
            KeyboardButton(text="❌cancel❌"),
        ],
        [
            KeyboardButton(text="🥙Mahsulotlar🥙"),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)
item = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🥙Mahsulotlar🥙"),
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)
