
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
import logging
import asyncio

BOT_TOKEN = "7871439975:AAFGN_Uxig2W3NhqhN8bNQlDCM10XnJahHg"
MANAGERS_CHAT_ID = -5028203828

class CarOrder(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    waiting_budget = State()
    waiting_models = State()
    waiting_year = State()
    waiting_mileage = State()
    waiting_additional = State()


bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

logging.basicConfig(level=logging.INFO)


def podbor_button():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Подбор Авто🚗",
                    url="https://t.me/KhanGroupPodborBot?start=podbor123",
                )
            ]
        ]
    )

@dp.message(CommandStart())
async def start_cmd(message: Message, state: FSMContext):
    args = message.text.split()

    if len(args) > 1:
        await message.answer("Заявка на подбор авто из Южной Кореи.\n\nНапиши своё имя:")
        await state.set_state(CarOrder.waiting_name)
        return

    await message.answer(
        "Привет! Это бот подбора авто из Кореи.\n\n"
        "Нажми кнопку под постом → начнём оформлять заявку.",
        reply_markup=podbor_button(),
    )


@dp.message(CarOrder.waiting_name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отправить номер☎", request_contact=True)],
            [KeyboardButton(text="Указать свой Telegram")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    await message.answer(
        "Теперь отправь номер телефона или укажи свой Telegram:",
        reply_markup=keyboard,
    )
    await state.set_state(CarOrder.waiting_phone)


@dp.message(CarOrder.waiting_phone)
async def get_phone(message: Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
    elif message.text == "Указать свой Telegram":
        if message.from_user.username:
            phone = f"@{message.from_user.username}"
        else:
            await message.answer(
                "У тебя не указан Telegram username.\n"
                "Напиши номер вручную:",
                reply_markup=ReplyKeyboardRemove(),
            )
            return
    else:
        phone = message.text.strip()

    await state.update_data(phone=phone)

    await message.answer(
        "Укажи бюджет в $ (например 15000–25000):",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(CarOrder.waiting_budget)


@dp.message(CarOrder.waiting_budget)
async def get_budget(message: Message, state: FSMContext):
    await state.update_data(budget=message.text.strip())
    await message.answer("Какие марки/модели интересны?")
    await state.set_state(CarOrder.waiting_models)


@dp.message(CarOrder.waiting_models)
async def get_models(message: Message, state: FSMContext):
    await state.update_data(models=message.text.strip())
    await message.answer("Год выпуска (например: от 2020)")
    await state.set_state(CarOrder.waiting_year)


@dp.message(CarOrder.waiting_year)
async def get_year(message: Message, state: FSMContext):
    await state.update_data(year=message.text.strip())
    await message.answer("Максимальный пробег (например: до 60000 км)")
    await state.set_state(CarOrder.waiting_mileage)


@dp.message(CarOrder.waiting_mileage)
async def get_mileage(message: Message, state: FSMContext):
    await state.update_data(mileage=message.text.strip())
    await message.answer(
        "Дополнительные пожелания (цвет, привод).\nИли напиши: без предпочтений"
    )
    await state.set_state(CarOrder.waiting_additional)


@dp.message(CarOrder.waiting_additional)
async def get_additional(message: Message, state: FSMContext):
    await state.update_data(additional=message.text.strip())
    data = await state.get_data()
    await state.clear()

    text = (
        "✨НОВАЯ ЗАЯВКА!✨\n\n"
        f"Имя: {data['name']}\n"
        f"Телефон: {data['phone']}\n"
        f"Бюджет: {data['budget']}$\n"
        f"Модели: {data['models']}\n"
        f"Год: {data['year']}\n"
        f"Пробег: {data['mileage']}\n"
        f"Доп. пожелания: {data['additional']}\n\n"
        f"ID клиента: {message.from_user.id}"
    )

    await bot.send_message(MANAGERS_CHAT_ID, text)

    await message.answer(
        "Заявка отправлена! Менеджер свяжется с тобой в течение 15–30 минут.",
        reply_markup=podbor_button(),
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
