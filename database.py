import sqlite3
import datetime


# 1. Функция создания базы (наш старый код)
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            username TEXT,
            join_date TEXT
        )
    """)
    conn.commit()
    conn.close()


# 2. НОВАЯ ФУНКЦИЯ: Добавление пользователя
def add_user(telegram_id, username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Получаем текущее время
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # Команда на добавление.
    # OR IGNORE означает: если такой telegram_id уже есть, просто проигнорируй и не выдавай ошибку
    cursor.execute(
        """
        INSERT OR IGNORE INTO users (telegram_id, username, join_date)
        VALUES (?, ?, ?)
    """,
        (telegram_id, username, now),
    )

    conn.commit()
    conn.close()


def count_users():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # SQL-команда: "Посчитай количество строк (*) в таблице users"
    cursor.execute("SELECT COUNT(*) FROM users")

    # Забираем ответ из базы (fetchone берет первый результат)
    result = cursor.fetchone()[0]

    conn.close()
    return result


def get_all_users():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Достаем только столбец telegram_id
    cursor.execute("SELECT telegram_id FROM users")

    # fetchall() забирает все найденные строки
    users = cursor.fetchall()
    conn.close()

    # База выдает данные в виде списка кортежей: [(123,), (456,)]
    # Эта строчка превращает их в обычный список: [123, 456]
    return [user[0] for user in users]


# Этот блок сработает только если мы запустим сам файл database.py
if __name__ == "__main__":
    init_db()  # Создаем таблицу
    add_user(123456, "Ivan_Firefighter")  # Пробуем добавить тестового Ивана
    add_user(
        123456, "Ivan_Firefighter"
    )  # Пробуем добавить его второй раз (сработает защита)

    print("Таблица создана, тестовый Иван добавлен!")
