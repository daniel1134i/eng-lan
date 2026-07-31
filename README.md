# Telegram English Learning Bot (aiogram 3.x + SQLite)

Полностью рабочий Telegram-бот для эффективного изучения 1025 самых популярных английских слов.

---

## 📁 Структура проекта

```text
eng-len/
├── .env.example              # Пример переменных окружения
├── requirements.txt          # Зависимости проекта
├── main.py                   # Точка входа (запуск бота и apscheduler)
├── seed_words.py             # Скрипт сидинга (заполнение БД 1025 словами)
├── bot.sqlite3               # База данных SQLite (создается автоматически)
│
├── config.py                 # Загрузка конфигураций из .env
│
├── database/                 # Работа с SQLite (aiosqlite)
│   ├── __init__.py
│   ├── db.py                 # Инициализация и подключение к БД
│   └── models.py             # Запросы и CRUD операции для users, words, user_words
│
├── keyboards/                # Интерактивные Inline и Reply клавиатуры
│   ├── __init__.py
│   └── inline.py             # Карточки, викторины, главное меню
│
├── handlers/                 # Обработчики команд и callback'ов
│   ├── __init__.py
│   ├── common.py             # /start, главное меню, статистика и профиль
│   ├── cards.py              # Режим флеш-карточек (переворот, "Уже знаю")
│   └── quiz.py               # Режим викторины (Multiple Choice 4 варианта)
│
└── services/                 # Сервисы и фоновые задачи
    ├── __init__.py
    └── scheduler.py          # Ежедневные напоминания и проверки (APScheduler)
```

---

## 🗄️ Схема базы данных (SQLite)

### 1. `users`
* `telegram_id` (INTEGER PRIMARY KEY) — Telegram ID пользователя.
* `created_at` (TIMESTAMP) — Дата регистрации.
* `streak_days` (INTEGER DEFAULT 0) — Дневной страйк активных занятий.
* `last_active_date` (TEXT) — Дата последней активности (`YYYY-MM-DD`).

### 2. `words`
* `word_id` (INTEGER PRIMARY KEY AUTOINCREMENT) — Уникальный ID слова.
* `english_word` (TEXT UNIQUE) — Слово на английском.
* `translation` (TEXT) — Перевод на русский.
* `part_of_speech` (TEXT) — Часть речи (noun, verb, adjective и т.д.).
* `example_sentence` (TEXT) — Пример предложения на английском с переводом.

### 3. `user_words`
* `user_id` (INTEGER) — Foreign Key на `users.telegram_id`.
* `word_id` (INTEGER) — Foreign Key на `words.word_id`.
* `status` (TEXT) — Статус (`'new'`, `'learning'`, `'learned'`).
* `next_review_at` (TIMESTAMP) — Дата следующего повторения.

---

## 🚀 Инструкция по запуску

### 1. Клонирование / Переход в папку
```bash
cd /Users/daniel/Documents/eng-len
```

### 2. Создание и активация виртуального окружения
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения (`.env`)
Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```
Откройте файл `.env` и укажите ваш токен бота от [@BotFather](https://t.me/BotFather):
```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

### 5. Первичная загрузка 1025 слов (Seeding script)
Запустите скрипт заполнения базы данных популярными английскими словами:
```bash
python seed_words.py
```

### 6. Запуск Telegram-бота
```bash
python main.py
```
