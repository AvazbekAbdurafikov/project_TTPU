
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import admin_id
from load_all import dp, bot
from states import NewItem
from database import Item, User


@dp.message_handler(user_id=admin_id, commands=["cancel"], state=NewItem)
async def cancel(message: types.Message, state: FSMContext):
    await message.answer("Siz Mahsulotni bekor qildingiz😒😒")
    await state.reset_state()


@dp.message_handler(user_id=admin_id, commands=["add_item"])
async def add_item(message: types.Message):
    await message.answer("Mahsulot nomini kiriting yoki 👉 /cancel ni bosing")
    await NewItem.Name.set()


@dp.message_handler(user_id=admin_id, state=NewItem.Name)
async def enter_name(message: types.Message, state: FSMContext):
    name = message.text
    item = Item()
    item.name = name

    await message.answer("Mahsulot nomi: {name}✅✅"
                           "\nMahsulot rasmini jo`nating yoki 👉 /cancel ni bosing".format(name=name))

    await NewItem.Photo.set()
    await state.update_data(item=item)


@dp.message_handler(user_id=admin_id, state=NewItem.Photo, content_types=types.ContentType.PHOTO)
async def add_photo(message: types.Message, state: FSMContext):
    photo = message.photo[-1].file_id
    data = await state.get_data()
    item: Item = data.get("item")
    item.photo = photo

    await message.answer_photo(
        photo=photo,
        caption="Mahsulot nomi: {name}✅✅"
                  "\nMahsulot narxini tiyinlarda yuboring💰💰 yoki 👉  /cancel ni bosing".format(name=item.name))

    await NewItem.Price.set()
    await state.update_data(item=item)


@dp.message_handler(user_id=admin_id, state=NewItem.Price)
async def enter_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item: Item = data.get("item")
    try:
        price = int(message.text)
    except ValueError:
        await message.answer("Noto`g`i qadam⚠️⚠, raqam kiriting")
        return

    item.price = price
    markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [InlineKeyboardButton(text="Ha👍", callback_data="confirm")],
            [InlineKeyboardButton(text="Qaytadan kiritish↩️", callback_data="change")],
        ]
    )
    await message.answer("Narxi: {price:,}\n"
                           "Tasdiqlaysizmi? \n Ortga qaytish uchun 👉 /cancel bosing".format(price=price / 100),
                         reply_markup=markup)
    await state.update_data(item=item)
    await NewItem.Confirm.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="change", state=NewItem.Confirm)
async def enter_price(call: types.CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.answer("Mahsulot narxini qaytadan kiriting")
    await NewItem.Price.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="confirm", state=NewItem.Confirm)
async def enter_price(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    data = await state.get_data()
    item: Item = data.get("item")
    await item.create()
    await call.message.answer("Mahsulot muvaffaqiyatli yakunlandi!✔️✔️ ")
    await state.reset_state()



@dp.message_handler(user_id=admin_id, commands=["tell_everyone"])
async def mailing(message: types.Message):
    await message.answer("Matn yuboring✈️✈️")
    await Mailing.Text.set()

