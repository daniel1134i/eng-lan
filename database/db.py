import aiosqlite
from config import DB_PATH

def get_db():
    return aiosqlite.connect(DB_PATH)


async def init_db():
    async with get_db() as db:
        db.row_factory = aiosqlite.Row

        # Таблица пользователей
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                streak_days INTEGER DEFAULT 1,
                last_active_date TEXT,
                reminder_hour INTEGER DEFAULT 9,
                selected_category TEXT DEFAULT 'all'
            )
        """)

        # Таблица слов
        await db.execute("""
            CREATE TABLE IF NOT EXISTS words (
                word_id INTEGER PRIMARY KEY AUTOINCREMENT,
                english_word TEXT UNIQUE NOT NULL,
                translation TEXT NOT NULL,
                part_of_speech TEXT,
                example_sentence TEXT,
                category TEXT DEFAULT 'Общие слова'
            )
        """)

        # Таблица связи пользователей и слов (Алгоритм SM-2)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_words (
                user_id INTEGER NOT NULL,
                word_id INTEGER NOT NULL,
                status TEXT DEFAULT 'new', -- 'new', 'learning', 'learned'
                next_review_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                interval INTEGER DEFAULT 0, -- Интервал в днях (SM-2)
                repetition_count INTEGER DEFAULT 0, -- Счетчик успехов (SM-2)
                ease_factor REAL DEFAULT 2.5, -- Коэффициент легкости (SM-2)
                PRIMARY KEY (user_id, word_id),
                FOREIGN KEY (user_id) REFERENCES users(telegram_id) ON DELETE CASCADE,
                FOREIGN KEY (word_id) REFERENCES words(word_id) ON DELETE CASCADE
            )
        """)

        # Таблица активности (Календарь занятий)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                user_id INTEGER NOT NULL,
                activity_date DATE DEFAULT (DATE('now')),
                PRIMARY KEY (user_id, activity_date)
            )
        """)

        # Миграции новых полей для слов и пользователей
        try:
            await db.execute("ALTER TABLE words ADD COLUMN synonyms TEXT")
        except Exception:
            pass

        try:
            await db.execute("ALTER TABLE words ADD COLUMN context_examples TEXT")
        except Exception:
            pass

        try:
            await db.execute("ALTER TABLE words ADD COLUMN is_custom INTEGER DEFAULT 0")
        except Exception:
            pass

        try:
            await db.execute("ALTER TABLE words ADD COLUMN user_id INTEGER DEFAULT NULL")
        except Exception:
            pass

        try:
            await db.execute("ALTER TABLE words ADD COLUMN movie_quote TEXT")
        except Exception:
            pass

        try:
            await db.execute("ALTER TABLE words ADD COLUMN video_url TEXT")
        except Exception:
            pass


        # Миграции полей если таблицы уже созданы

        try:
            await db.execute("ALTER TABLE users ADD COLUMN reminder_hour INTEGER DEFAULT 9")
        except Exception:
            pass
            
        try:
            await db.execute("ALTER TABLE users ADD COLUMN pack_start_date TIMESTAMP DEFAULT NULL")
        except Exception:
            pass

        try:
            await db.execute("ALTER TABLE users ADD COLUMN words_added_this_pack INTEGER DEFAULT 0")
        except Exception:
            pass
            
        # Таблица PvP дуэлей
        await db.execute("""
            CREATE TABLE IF NOT EXISTS duels (
                duel_id TEXT PRIMARY KEY,
                creator_id INTEGER NOT NULL,
                creator_name TEXT,
                opponent_id INTEGER DEFAULT NULL,
                opponent_name TEXT DEFAULT NULL,
                words_json TEXT NOT NULL,
                creator_score INTEGER DEFAULT 0,
                opponent_score INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending', -- 'pending', 'active', 'finished'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.commit()

