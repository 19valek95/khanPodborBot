
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
import asyncio
import logging
import os
from aiohttp import web

# === ТВОЙ ТОКЕН ===
BOT_TOKEN = "7871439975:AAGjA2k5HOMxL99kzhivbKHNcolQYIsOsAE"

# === ID группы менеджеров ===
MANAGERS_CHAT_ID = -5028203828

# === Состояния ===
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


# Кнопка "подбор"
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


# Команда start
@dp.message(CommandStart())
async def start_cmd(message: Message, state: FSMContext):
    args = message.text.split()

    # Если старт через ссылку с параметром
    if len(args) > 1:
        await message.answer(
            "Заявка на подбор авто из Южной Кореи.\n\nНапиши своё имя:"
        )
        await state.set_state(CarOrder.waiting_name)
        return

    # Обычный старт
    await message.answer(
        "Привет! Это бот подбора авто из Кореи.\n\n"
        "Нажми кнопку под постом → начнём оформлять заявку.",
        reply_markup=podbor_button(),
    )


# Имя
@dp.message(CarOrder.waiting_name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())

    # Клавиатура с двумя кнопками:
    # 1) отправить контакт
    # 2) указать свой Telegram
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Отправить номер☎", request_contact=True),
            ],
            [
                KeyboardButton(text="Указать свой Telegram"),
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    await message.answer(
        "Теперь отправь номер телефона или укажи свой Telegram:",
        reply_markup=keyboard,
    )
    await state.set_state(CarOrder.waiting_phone)


# Телефон / Telegram
@dp.message(CarOrder.waiting_phone)
async def get_phone(message: Message, state: FSMContext):
    # Если пользователь нажал "Отправить номер" и прислал контакт
    if message.contact:
        phone = message.contact.phone_number
    # Если нажал "Указать свой Telegram"
    elif message.text == "Указать свой Telegram":
        if message.from_user.username:
            phone = f"@{message.from_user.username}"
        else:
            # Если у пользователя нет username
            await message.answer(
                "У тебя не указан Telegram username в профиле.\n"
                "Пожалуйста, напиши номер телефона вручную:",
                reply_markup=ReplyKeyboardRemove(),
            )
            # остаёмся в том же состоянии waiting_phone
            return
    else:
        # Любой другой текст – считаем введённым номером
        phone = message.text.strip()

    await state.update_data(phone=phone)

    await message.answer(
        "Укажи бюджет в $💰 (например: 15000-25000):",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(CarOrder.waiting_budget)


# Бюджет
@dp.message(CarOrder.waiting_budget)
async def get_budget(message: Message, state: FSMContext):
    await state.update_data(budget=message.text.strip())
    await message.answer("Какие марки/модели интересны?")
    await state.set_state(CarOrder.waiting_models)


# Модели
@dp.message(CarOrder.waiting_models)
async def get_models(message: Message, state: FSMContext):
    await state.update_data(models=message.text.strip())
    await message.answer("Год выпуска (например: от 2020)")
    await state.set_state(CarOrder.waiting_year)


# Год
@dp.message(CarOrder.waiting_year)
async def get_year(message: Message, state: FSMContext):
    await state.update_data(year=message.text.strip())
    await message.answer("Максимальный пробег (например: до 60 000 км)")
    await state.set_state(CarOrder.waiting_mileage)


# Пробег
@dp.message(CarOrder.waiting_mileage)
async def get_mileage(message: Message, state: FSMContext):
    await state.update_data(mileage=message.text.strip())
    await message.answer(
        "❗Дополнительные пожелания❗(цвет, привод и т.д.)\n"
        "Или напиши «без предпочтений»."
    )
    await state.set_state(CarOrder.waiting_additional)


# Пожелания
@dp.message(CarOrder.waiting_additional)
async def get_additional(message: Message, state: FSMContext):
    await state.update_data(additional=message.text.strip())
    data = await state.get_data()
    await state.clear()

    # Сообщение менеджеру
    text = (
        "✨НОВАЯ ЗАЯВКА!✨\n\n"
        f"Имя: {data['name']}\n"
        f"Телефон / Telegram: {data['phone']}\n"
        f"Бюджет: {data['budget']} $\n"
        f"Модели: {data['models']}\n"
        f"Год: {data['year']}\n"
        f"Пробег max: {data['mileage']}\n"
        f"Доп. пожелания: {data['additional']}\n\n"
        f"ID клиента: {message.from_user.id}"
    )

    await bot.send_message(MANAGERS_CHAT_ID, text)

    await message.answer(
        "Заявка успешно отправлена!\nМенеджер свяжется с тобой "
        "в течение 15–30 минут.",
        reply_markup=podbor_button(),
    )


# ======= простой веб‑сервер для Render =======
async def handle(request):
    return web.Response(text="Bot is running")


async def run_web_app():
    app = web.Application()
    app.router.add_get("/", handle)

    port = int(os.environ.get("PORT", 10000))  # Render передаст сюда свой порт
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Web server started on port {port}")


async def main():
    print("Бот @KhanGroupPodborBot запускается...")
    # параллельно запускаем веб‑сервер и polling бота
    await asyncio.gather(
        run_web_app(),
        dp.start_polling(bot),
    )


if __name__ == "__main__":
    asyncio.run(main())




