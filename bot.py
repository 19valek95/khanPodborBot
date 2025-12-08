from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram import F
import asyncio

TOKEN = "ВАШ_ТОКЕН"
ADMIN_ID = 123456789  # ID куда отправлять заявки

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ------------------ FSM ------------------

class Form(StatesGroup):
    marka = State()
    model = State()
    year = State()
    budget = State()
    region = State()
    contact = State()   # <-- ВАЖНО: контакт спрашиваем в самом конце


# ------------------ HANDLERS ------------------

@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await message.answer("Здравствуйте! Давайте подберём вам авто.\n\nВведите марку автомобиля:")
    await state.set_state(Form.marka)


@dp.message(Form.marka)
async def get_marka(message: Message, state: FSMContext):
    await state.update_data(marka=message.text)
    await message.answer("Введите модель автомобиля:")
    await state.set_state(Form.model)


@dp.message(Form.model)
async def get_model(message: Message, state: FSMContext):
    await state.update_data(model=message.text)
    await message.answer("Введите год выпуска:")
    await state.set_state(Form.year)


@dp.message(Form.year)
async def get_year(message: Message, state: FSMContext):
    await state.update_data(year=message.text)
    await message.answer("Ваш желаемый бюджет?")
    await state.set_state(Form.budget)


@dp.message(Form.budget)
async def get_budget(message: Message, state: FSMContext):
    await state.update_data(budget=message.text)
    await message.answer("Из какого вы региона?")
    await state.set_state(Form.region)


@dp.message(Form.region)
async def get_region(message: Message, state: FSMContext):
    await state.update_data(region=message.text)

    # Финальный шаг
    await message.answer("Спасибо! Последний вопрос:\n\n"
                         "📞 Оставьте ваш номер телефона или @Telegram для связи:")
    await state.set_state(Form.contact)


@dp.message(Form.contact)
async def get_contact(message: Message, state: FSMContext):
    await state.update_data(contact=message.text)
    data = await state.get_data()

    # Формируем заявку
    text = (
        "📩 *Новая заявка на подбор авто:*\n\n"
        f"🔹 Марка: {data['marka']}\n"
        f"🔹 Модель: {data['model']}\n"
        f"🔹 Год: {data['year']}\n"
        f"🔹 Бюджет: {data['budget']}\n"
        f"🔹 Регион: {data['region']}\n"
        f"📞 Контакт: {data['contact']}"
    )

    # Отправляем админу
    await bot.send_message(ADMIN_ID, text, parse_mode="Markdown")

    await message.answer("Спасибо! Ваша заявка отправлена. Наш специалист свяжется с вами в ближайшее время.")
    await state.clear()


# ------------------ RUN ------------------

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())



