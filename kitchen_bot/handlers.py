import asyncio
import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import (Message, InlineKeyboardMarkup, InlineKeyboardButton,
                           CallbackQuery, LabeledPrice, PreCheckoutQuery, pre_checkout_query)
from aiogram.utils.callback_data import CallbackData
from keyboards import markup
import database
import states
from config import lp_token, admin_id
from load_all import dp, bot

db = database.DBCommands()

# Используем CallbackData для работы с коллбеками, в данном случае для работы с покупкой товаров
buy_item = CallbackData("buy", "item_id")


# Для команды /start есть специальный фильтр, который можно тут использовать
@dp.message_handler(CommandStart())
async def register_user(message: types.Message):
    chat_id = message.from_user.id
    referral = message.get_args()
    user = await db.add_new_user(referral=referral)
    id = user.id
    count_users = await db.count_users()

    # Отдадим пользователю клавиатуру с выбором языков
    # languages_markup = InlineKeyboardMarkup(
    #     inline_keyboard=
    #     [
    #         [
    #             InlineKeyboardButton(text="Русский", callback_data="lang_ru")],
    #         [
    #             InlineKeyboardButton(text="English", callback_data="lang_en"),
    #             InlineKeyboardButton(text="O`zbek", callback_data="lang_uz"),
    #         ]
    #     ]
    # )

    bot_username = (await bot.me).username
    bot_link = f"https://t.me/{bot_username}?start={id}"

    # Для многоязычности, все тексты, передаваемые пользователю должны передаваться в функцию "_"
    # Вместо "текст" передаем _("текст")

    text = ("Xush kelibsiz!!\n"
            # "Сейчас в базе {count_users} человек!\n"
             "Sizning refral havolangiz✔️✔️: {bot_link}\n"
             "Referalingizni ushbu kamanda orqali aniqlashingiz mumkin: /referrals\nMahsulotlarni ko`rish🆓: /items\n").format(
        count_users=count_users,
        bot_link=bot_link
    )
    if message.from_user.id == admin_id:
        text += "Yangi mahsulot🥙 qo`shish: /add_item"
    await bot.send_message(chat_id, text)# reply_markup=languages_markup)



@dp.message_handler(commands=["referrals"])
async def check_referrals(message: types.Message):
    referrals = await db.check_referrals()
    text = "\nSiznig referallaringiz✔✔:\n{referrals}".format(referrals=referrals)
    await message.answer(text)


# Показываем список доступных товаров
@dp.message_handler(commands=["items"])
async def show_items(message: Message):
    # Достаем товары из базы данных
    all_items = await db.show_items()
    # Проходимся по товарам, пронумеровывая
    for num, item in enumerate(all_items):
        text = "<b>Mahsulot</b> \t№{id}: <u>{name}</u>\n<b>Narxi💸:</b> \t{price:,}"
        markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    # Создаем кнопку "купить" и передаем ее айдишник в функцию создания коллбека
                    InlineKeyboardButton(text="💵Xarid qilish💵", callback_data=buy_item.new(item_id=item.id))
                ],
            ]
        )

        # Отправляем фотку товара с подписью и кнопкой "купить"
        await message.answer_photo(
            photo=item.photo,
            caption=text.format(
                id=item.id,
                name=item.name,
                price=item.price / 100
            ),
            reply_markup=markup
        )
        # Между сообщениями делаем небольшую задержку, чтобы не упереться в лимиты
        await asyncio.sleep(0.3)



@dp.callback_query_handler(buy_item.filter())
async def buying_item(call: CallbackQuery, callback_data: dict, state: FSMContext):
    # То, что мы указали в CallbackData попадает в хендлер под callback_data, как словарь, поэтому достаем айдишник
    item_id = int(callback_data.get("item_id"))
    await call.message.edit_reply_markup()

    # Mahsulotni bazadan olamiz
    item = await database.Item.get(item_id)
    if not item:
        await call.message.answer("Bu Mahsulot mavjud emas😔😔")
        return

    text = "Mahsulot \"<b>{name}</b>\" Narxi: <i>{price:,}/dona.</i>Mahsulot miqdorini kiriting yoki /cancel ni bosing".format(name=item.name,
                                                             price=item.price / 100)
    await call.message.answer(text)
    await states.Purchase.EnterQuantity.set()

    # Сохраняем в ФСМ класс товара и покупки
    await state.update_data(
        item=item,
        purchase=database.Purchase(
            item_id=item_id,
            purchase_time=datetime.datetime.now(),
            buyer=call.from_user.id
        )
    )


# Принимаем в этот хендлер только цифры
@dp.message_handler(regexp=r"^(\d+)$", state=states.Purchase.EnterQuantity)
async def enter_quantity(message: Message, state: FSMContext):
    # Получаем количество указанного товара
    quantity = int(message.text)
    async with state.proxy() as data:  # Работаем с данными из ФСМ
        data["purchase"].quantity = quantity
        item = data["item"]
        amount = item.price * quantity
        data["purchase"].amount = amount

    # # Создаем кнопки
    # agree_button = InlineKeyboardButton(
    #     text="Roziman😊",
    #     callback_data="agree"
    # )
    # change_button = InlineKeyboardButton(
    #     text="Qaytadan qiymat kiritish↩️↩️",
    #     callback_data="change"
    # )
    # cancel_button = InlineKeyboardButton(
    #     text="Bekor qilish❎",
    #     callback_data="cancel"
    # )
    #
    # # Создаем клавиатуру
    # markup = InlineKeyboardMarkup(
    #     inline_keyboard=
    #     [
    #         [agree_button],  # Первый ряд кнопок
    #         [change_button],  # Второй ряд кнопок
    #         [cancel_button]  # Третий ряд кнопок
    #     ]
    # )
    await message.answer(
        "Yaxshi, Siz<i>{quantity}</i> {name}ni  <b>{price:,}💵narxda sotib olyapsiz.</b>\n\n"
          "Ummumiy<b>{amount:,}ta</b>. Tasdiqlaysizmi?".format(
            quantity=quantity,
            name=item.name,
            amount=amount / 100,
            price=item.price / 100
        ),
        reply_markup=markup)
    await states.Purchase.Approval.set()


# То, что не является числом - не попало в предыдущий хендлер и попадает в этот
@dp.message_handler(state=states.Purchase.EnterQuantity)
async def not_quantity(message: Message):
    await message.answer("🔴Noto`g`ri harakat🔴, mahsulot miqdorini kiriting ")


# Если человек нажал на кнопку Отменить во время покупки - убираем все
@dp.callback_query_handler(text_contains="cancel", state=states.Purchase)
async def approval(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()  # Убираем кнопки
    await call.message.answer("Siz bu xaridni bekor qildingiz🚫!")
    await state.reset_state()


# Если человек нажал "ввести заново"
@dp.callback_query_handler(text_contains="change", state=states.Purchase.Approval)
async def approval(call: CallbackQuery):
    await call.message.edit_reply_markup()  # Убираем кнопки
    await call.message.answer("‼️Mahsulot miqdorini kiriting‼️.")
    await states.Purchase.EnterQuantity.set()


# Если человек нажал "согласен"
@dp.callback_query_handler(text_contains="agree", state=states.Purchase.Approval)
async def approval(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()  # Убираем кнопки

    data = await state.get_data()
    purchase: database.Purchase = data.get("purchase")
    item: database.Item = data.get("item")
    # Теперь можно внести данные о покупке в базу данных через .create()
    await purchase.create()
    await bot.send_message(chat_id=call.from_user.id,
                           text="Umumiy<b>{amount:,}</b> \nQuyidagi tugma orqali to`lang 👇👇".format(amount=purchase.amount))
    ################
    # --Ниже выбрать нужные параметры--
    # Пример заполнения можно посмотреть тут https://surik00.gitbooks.io/aiogram-lessons/content/chapter4.html
    # Но прошу обратить внимание, те уроки по старой версии aiogram и давно не обновлялись, так что могут быть
    # несостыковки.
    ################
    currency = "UZS"
    need_name = True
    need_phone_number = False
    need_email = False
    need_shipping_address = True

    await bot.send_invoice(chat_id=call.from_user.id,
                           title=item.name,
                           description=item.name,
                           payload=str(purchase.id),
                           start_parameter=str(purchase.id),
                           currency=currency,
                           prices=[
                               LabeledPrice(label=item.name, amount=purchase.amount)
                           ],
                           provider_token=lp_token,
                           need_name=need_name,
                           need_phone_number=need_phone_number,
                           need_email=need_email,
                           need_shipping_address=need_shipping_address
                           )
    await state.update_data(purchase=purchase)
    await states.Purchase.Payment.set()


@dp.pre_checkout_query_handler(state=states.Purchase.Payment)
async def checkout(query: PreCheckoutQuery, state: FSMContext):
    await bot.answer_pre_checkout_query(query.id, True)
    data = await state.get_data()
    purchase: database.Purchase = data.get("purchase")
    success = await check_payment(purchase)

    if success:
        await purchase.update(
            successful=True,
            shipping_address=query.order_info.shipping_address.to_python()
            if query.order_info.shipping_address
            else None,
            phone_number=query.order_info.phone_number,
            receiver=query.order_info.name,
            email=query.order_info.email
        ).apply()
        await state.reset_state()
        await bot.send_message(query.from_user.id, "😊Xarid uchun raxmat😊")
        await bot.send_message(chat_id=admin_id, text=f"telefon raqam: {purchase.phone_number}\n"
                               f"id: {purchase.id}\n"
                               f"To`lov miqdori: {purchase.amount}\n"
                               f"Sotib olingan vaqti: {purchase.purchase_time}\n"
                               f"Sotib oluvchi: {purchase.buyer}\n"
                               f"Mahsulot Id si: {purchase.item_id}\n"
                               f"Muvafaqiyatli?: {purchase.successful}\n"
                               f"Oluvchi: {purchase.receiver}\n"
                               f"Olish manzili: {purchase.shipping_address}\n"
                               f"Miqdori: {purchase.quantity}\n")
    else:
        await bot.send_message(query.from_user.id, "Xatolik yuz berdi🚫 keyinroq urunib ko`ring!")

async def other_echo(message: Message):
    await message.answer(message.text)


async def check_payment(purchase: database.Purchase):
    return True

