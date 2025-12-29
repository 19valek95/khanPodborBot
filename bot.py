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
    waiting_data = State()  # Один стейт для ввода всех данных

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
        "• Подготовка авто к экспорту, документы, таможня\n"
        "• Доставка в вашу страну, город\n"
        "• Полное сопровождение сделки, прозрачность, видеоотчёты",
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
    await call.message.answer(
        "🚗 *Оставьте заявку на подбор авто*\n\n"
        "Пожалуйста, отправьте одним сообщением в формате:\n\n"
        "*Имя, Модель автомобиля, Контакт*\n\n"
        "Пример:\n"
        "Иван, Kia Sorento, +79991234567\n"
        "или\n"
        "Анна, Hyundai Tucson, @anna_telegram",
        parse_mode="Markdown"
    )
    await state.set_state(Form.waiting_data)

# ---------- ОБРАБОТКА СООБЩЕНИЯ С ДАННЫМИ ЧЕРЕЗ ЗАПЯТУЮ ----------
@dp.message(Form.waiting_data)
async def process_request(message: Message, state: FSMContext):
    text = message.text.strip()
    parts = [part.strip() for part in text.split(',', 2)]  # Разделяем максимум на 3 части

    if len(parts) < 3:
        await message.answer(
            "❌ Пожалуйста, укажите все три поля через запятую:\n"
            "Имя, Модель автомобиля, Контакт\n\n"
            "Пример: Иван, Kia Sorento, +79991234567\n"
            "Попробуйте ещё раз."
        )
        return

    name = parts[0]
    model = parts[1]
    contact = parts[2]

    # Формируем сообщение администратору
    admin_text = (
        "📩 *Новая заявка на подбор авто:*\n\n"
        f"👤 Имя: {name}\n"
        f"🚗 Модель: {model}\n"
        f"📞 Контакт: {contact}"
    )

    await bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")

    # Ответ пользователю
    await message.answer(
        "✅ Спасибо, заявка принята!\n"
        "Наш специалист свяжется с вами в ближайшее время 🙌"
    )

    # Возвращаем на главный экран
    await show_main_menu(message, state)

# ---------- RUN ----------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())






