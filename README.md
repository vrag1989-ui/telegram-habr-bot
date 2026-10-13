# 🤖 Telegram News & Crypto Bot

Многофункциональный Telegram-бот на Python с автоматическим парсингом новостей, интеграцией внешних API, базой данных SQLite и админ-панелью.

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://python.org)
[![aiogram](https://img.shields.io/badge/aiogram-3.x-informational?logo=telegram)](https://github.com/aiogram/aiogram)
[![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey?logo=sqlite)](https://sqlite.org)
[![Status](<https://img.shields.io/badge/Deployment-Timeweb_Cloud_(Ubuntu)-brightgreen>)](#)

---

## 🚀 Основные возможности

- 📰 **Парсинг Хабра:** Сбор свежих IT-статей в реальном времени с помощью BeautifulSoup4.
- ⏰ **Утренняя авторассылка:** Ежедневная отправка свежего дайджеста новостей по расписанию (APScheduler).
- 💰 **Курс криптовалют (API):** Получение актуального курса Bitcoin через REST API блокчейна.
- 💬 **Обратная связь (FSM):** Реализация машины состояний для отправки сообщений администратору бота.
- 🗄 **База данных:** Автоматическая регистрация пользователей при старте (sqlite3).
- 📢 **Панель администратора:**
  - Просмотр статистики аудитории (/stats).
  - Массовая рассылка сообщений всем пользователям (/broadcast).

---

## 🛠 Стек технологий

- **Язык:** Python 3.12
- **Фреймворк:** aiogram 3.x (асинхронная архитектура)
- **Парсинг:** BeautifulSoup4, Requests
- **База данных:** SQLite3
- **Планировщик:** APScheduler
- **Инфраструктура:** VPS Timeweb Cloud (Ubuntu Linux), фоновый сервис systemd (24/7).

---

## ⚙️ Установка и запуск

1. Клонировать репозиторий:
   git clone https://github.com/vrag1989-ui/telegram-habr-bot.git
   cd telegram-habr-bot

2. Создать виртуальное окружение:
   python -m venv venv
   source venv/bin/activate # Linux
   venv\Scripts\activate # Windows

3. Установить зависимости:
   pip install aiogram requests beautifulsoup4 python-dotenv apscheduler

4. Создать файл .env с токеном:
   BOT*TOKEN=ваш*токен

5. Запустить бота:
   python parser_bot.py
