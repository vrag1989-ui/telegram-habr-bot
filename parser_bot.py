import asyncio
import os
import csv
import requests
from database import init_db, add_user, count_users, get_all_users
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    LabeledPrice,
)
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler


class Feedback(StatesGroup):
    waiting_for_message = State()  # Это наш ярлык: "Ждем сообщение от пользователя"


# Загружаем токен из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Свежие статьи")],
        [KeyboardButton(text="📈 Статистика")],
        [KeyboardButton(text="💬 Написать админу")],
        [KeyboardButton(text="💰 Курс Биткоина")],
        [KeyboardButton(text="⭐ VIP-подписка")],
    ],
    resize_keyboard=True,
)

about_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        # url - это ссылка, которая откроется при нажатии
        [InlineKeyboardButton(text="🚀 Мой будущий GitHub", url="https://github.com/")]
    ]
)


def get_habr_news():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get("https://habr.com/ru/articles/", headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("article")

    result_text = "🌅 Утренний IT-кофе! Топ-5 свежих статей с Хабра:\n\n"

    for block in articles[:5]:
        link_tag = block.find("a", class_="tm-title__link")
        if link_tag:
            title = link_tag.text
            link = "https://habr.com" + link_tag.get("href")
            result_text += f"🔹 {title}\n🔗 {link}\n\n"

    return result_text


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    add_user(message.from_user.id, message.from_user.username)

    # 1. Ваше старое сообщение (оно включает нижние кнопки)
    await message.answer("Привет! Я бот-парсер 🤖", reply_markup=main_kb)

    # 2. НОВОЕ сообщение с прилепленной прозрачной кнопкой
    await message.answer("Здесь скоро будет лежать мой код:", reply_markup=about_kb)


@dp.message(F.text == "📈 Статистика")
async def cmd_stats(message: types.Message):
    # Сюда мы впишем ваш ID. Пока напишем наугад:
    ADMIN_ID = 280307127

    # Если ID того, кто написал, совпадает с ID админа:
    if message.from_user.id == ADMIN_ID:
        total = count_users()
        await message.answer(
            f"📊 Статистика бота:\nЗарегистрировано пользователей: {total}"
        )

    # Если ID чужой:
    else:
        # Бот отругает и заодно любезно подскажет ваш настоящий ID :)
        await message.answer(
            f"⛔️ У вас нет прав администратора!\nВаш Telegram ID: {message.from_user.id}"
        )


@dp.message(Command("broadcast"))
async def cmd_broadcast(message: types.Message):
    ADMIN_ID = 280307127  # ВАШ НАСТОЯЩИЙ ID

    if message.from_user.id == ADMIN_ID:
        # 1. Отрезаем слово "/broadcast " от сообщения, чтобы оставить только сам текст рассылки
        text_to_send = message.text.replace("/broadcast ", "")

        # 2. Берем список всех людей
        users = get_all_users()
        success_count = 0

        # 3. Перебираем их по одному и отправляем текст
        for user_id in users:
            try:
                # ВАЖНО: bot.send_message умеет отправлять сообщение ЛЮБОМУ человеку по его ID
                await bot.send_message(user_id, text_to_send)
                success_count += 1
            except Exception:
                # Если человек заблокировал бота, Питон выдаст ошибку.
                # Эта конструкция (try/except) просто проигнорирует ошибку и пойдет к следующему человеку.
                pass

        await message.answer(f"✅ Рассылка завершена! Доставлено: {success_count} чел.")
    else:
        await message.answer("⛔️ У вас нет прав.")


# Обработчик нашей главной команды
@dp.message(F.text == "📊 Свежие статьи")
async def cmd_scrape(message: types.Message):
    # Просто просим функцию-помощника собрать новости
    news = get_habr_news()

    # И отправляем результат в чат
    await message.answer(news, disable_web_page_preview=True)


# 1. Функция, которая реагирует на кнопку и ВКЛЮЧАЕТ режим ожидания
@dp.message(F.text == "💬 Написать админу")
async def feedback_start(message: types.Message, state: FSMContext):
    await message.answer("Напишите ваше сообщение, и я передам его создателю бота:")

    # Вешаем на человека ярлык (включаем режим)
    await state.set_state(Feedback.waiting_for_message)


# 2. Функция, которая ловит текст ТОЛЬКО если включен режим ожидания
@dp.message(F.text == "💰 Курс Биткоина")
async def get_bitcoin(message: types.Message):
    # Притворяемся браузером
    headers = {"User-Agent": "Mozilla/5.0"}

    # Стучимся к старейшему API блокчейна
    response = requests.get("https://blockchain.info/ticker", headers=headers)

    try:
        # Пытаемся расшифровать JSON
        data = response.json()

        # У blockchain.info цена спрятана в словаре так:
        price = data["USD"]["last"]

        await message.answer(f"📈 Текущий курс Bitcoin: {price} $")

    except Exception as e:
        # Если сайт нас заблокировал, Питон не упадет, а пришлет текст ошибки прямо в чат!
        error_msg = f"⛔️ Ошибка доступа!\nКод: {response.status_code}\nТекст сайта: {response.text[:200]}"
        await message.answer(error_msg)


# Отправляем "счёт" (invoice) при нажатии на кнопку
@dp.message(F.text == "⭐ VIP-подписка")
async def send_stars_invoice(message: types.Message):
    await message.answer_invoice(
        title="VIP-подписка на 30 дней",
        description="Доступ к эксклюзивным IT-новостям и аналитике 🔥",
        payload="vip_30_days",  # Секретная метка для нас (пользователь её не видит)
        currency="XTR",  # XTR — это код валюты Telegram Stars
        prices=[LabeledPrice(label="VIP", amount=1)],  # Цена: 1 звезда (для теста)
    )


# Ловим успешную оплату
@dp.message(F.successful_payment)
async def on_successful_payment(message: types.Message):
    # Сюда Телеграм автоматически пришлёт сообщение, когда человек оплатит
    await message.answer(
        "🎉 Оплата прошла! Добро пожаловать в VIP-клуб!\nСпасибо за поддержку! 🙏"
    )


async def send_morning_message(bot: Bot):
    ADMIN_ID = 280307127  # ВАЖНО: Впишите сюда ваш настоящий Telegram ID!

    news = get_habr_news()

    # Бот пишет вам напрямую по вашему ID:
    await bot.send_message(ADMIN_ID, news, disable_web_page_preview=True)


async def main():
    init_db()  # <-- Добавили вот эту строчк
    print("Parser Bot is running!")

    # 1. Создаем механизм (я специально указал ваш часовой пояс - Томск!)
    scheduler = AsyncIOScheduler(timezone="Asia/Tomsk")

    # --- БОЕВОЙ РЕЖИМ (каждый день в 09:00 утра) ---
    scheduler.add_job(
        send_morning_message, "cron", hour=9, minute=0, kwargs={"bot": bot}
    )

    # 2. Включаем тиканье часов
    scheduler.start()

    # ... дальше идет ваш старый код ...
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
