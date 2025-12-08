from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F
import asyncio

TOKEN = "7871439975:AAFGN_Uxig2W3NhqhN8bNQlDCM10XnJahHg"
ADMIN_ID = -5028203828

bot = Bot(token=TOKEN)
dp = Dispatcher()

class Form(StatesGroup):
    name = State()
    marka = State()
    model = State()
    year = State()
    budget = State()
    region = State()
    contact = State()


# ---------- ФУНКЦИЯ ГЛАВНОГО ЭКРАНА ----------

async def show_main_menu(message: Message, state: FSMContext):
    banner = FSInputFile("banner.png")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚗 Оставить заявку", callback_data="leave_request")],
        [InlineKeyboardButton(text="📋 Наши услуги", callback_data="services")],
        [InlineKeyboardButton(text="📞 Контакты", callback_data="contacts")]
    ])

    await message.answer_photo(
        banner,
        caption=(
            "Добро пожаловать в *K-HAN Motors!* 🇰🇷\n\n"
            "Мы поможем подобрать автомобиль под ваш бюджет и пожелания.\n\n"
            "Выберите действие ниже 👇"
        ),
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await state.clear()


# ---------- /start ----------

@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await show_main_menu(message, state)


# ---------- INLINE HANDLERS ----------

@dp.callback_query(F.data == "services")
async def services(call: types.CallbackQuery):
    await call.message.answer(
        "📋 *Наши услуги:*\n"
        "• Подбор авто в Корее\n"
        "• Проверка по страховым базам, ДТП, ремонтные работы\n"
        "• Подготовка авто к экспорту , документы, таможня\n"
        "• Доставка в вашу страну, город\n"
        "• Полное сопровождение сделки, прозрачность, видиоотчеты",
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "contacts")
async def contacts(call: types.CallbackQuery):
    await call.message.answer(
        "📞 *Контакты:*\n"
        "Telegram: @valpak95\n"
        "Телефон: +821084700073,\n+821023118899",
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "leave_request")
async def leave_request(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Для начала введите ваше *имя*:", parse_mode="Markdown")
    await state.set_state(Form.name)


# ---------- COLLECTING FORM DATA (как у тебя) ----------

@dp.message(Form.name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите марку автомобиля:")
    await state.set_state(Form.marka)

@dp.message(Form.marka)
async def get_marka(message: Message, state: FSMContext):
    await state.update_data(marka=message.text)
    await message.answer("Введите модель автомобиля:")
    await state.set_state(Form.model)

@dp.message(Form.model)
async def get_model(message: Message, state: FSMContext):
    await state.update_data(model=message.text)
    await message.answer("Введите предпочитаемый год выпуска:")
    await state.set_state(Form.year)

@dp.message(Form.year)
async def get_year(message: Message, state: FSMContext):
    await state.update_data(year=message.text)
    await message.answer("Ваш желаемый бюджет?\nВ Рублях|₽| или Долларах|$|")
    await state.set_state(Form.budget)

@dp.message(Form.budget)
async def get_budget(message: Message, state: FSMContext):
    await state.update_data(budget=message.text)
    await message.answer("Из какого вы региона, города?")
    await state.set_state(Form.region)

@dp.message(Form.region)
async def get_region(message: Message, state: FSMContext):
    await state.update_data(region=message.text)
    await message.answer(
        "📞 Последний шаг!\n\n"
        "Оставьте ваш номер телефона или @Telegram:"
    )
    await state.set_state(Form.contact)

@dp.message(Form.contact)
async def get_contact(message: Message, state: FSMContext):
    await state.update_data(contact=message.text)
    data = await state.get_data()

    text = (
        "📩 *Новая заявка на подбор авто:*\n\n"
        f"👤 Имя: {data['name']}\n"
        f"🚗 Марка: {data['marka']}\n"
        f"🚘 Модель: {data['model']}\n"
        f"📅 Год: {data['year']}\n"
        f"💰 Бюджет: {data['budget']}\n"
        f"🌍 Регион: {data['region']}\n"
        f"📞 Контакт: {data['contact']}"
    )

    await bot.send_message(ADMIN_ID, text, parse_mode="Markdown")

    await message.answer(
        "Спасибо! Ваша заявка отправлена.\n"
        "Наш специалист свяжется с вами в ближайшее время 🙌"
    )

    # после опроса показываем главный экран
    await show_main_menu(message, state)


# ---------- RUN ----------

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())







