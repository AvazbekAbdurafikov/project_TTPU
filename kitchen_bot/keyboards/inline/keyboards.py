from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

buy_item = CallbackData("buy", "item_id")

agree_button = InlineKeyboardButton(
    text="Roziman😊",
    callback_data="agree"
)
change_button = InlineKeyboardButton(
    text="Qaytadan qiymat kiritish↩️↩️",
    callback_data="change"
)
cancel_button = InlineKeyboardButton(
    text="Bekor qilish❎",
    callback_data="cancel"
)

markup = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [agree_button],  # Первый ряд кнопок
        [change_button],  # Второй ряд кнопок
        [cancel_button]  # Третий ряд кнопок
    ]
)
