import aiosqlite
from datetime import datetime, date, timedelta
from database.db import get_db


# ----------------- USERS -----------------

async def get_or_create_user(telegram_id: int):
    today_str = date.today().isoformat()
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
            user = await cursor.fetchone()
        
        if not user:
            await db.execute(
                "INSERT INTO users (telegram_id, streak_days, last_active_date) VALUES (?, 1, ?)",
                (telegram_id, today_str)
            )
            await db.commit()
            # Назначаем пользователю все существуюшие слова в статус 'new'
            await db.execute("""
                INSERT OR IGNORE INTO user_words (user_id, word_id, status)
                SELECT ?, word_id, 'new' FROM words
            """, (telegram_id,))
            await db.commit()
            
            async with db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
                user = await cursor.fetchone()
        else:
            # Обновляем страйк
            last_active = user['last_active_date']
            streak = user['streak_days']
            if last_active:
                last_date = date.fromisoformat(last_active)
                if last_date == date.today() - timedelta(days=1):
                    streak += 1
                    await db.execute(
                        "UPDATE users SET streak_days = ?, last_active_date = ? WHERE telegram_id = ?",
                        (streak, today_str, telegram_id)
                    )
                    await db.commit()
                elif last_date < date.today() - timedelta(days=1):
                    streak = 1
                    await db.execute(
                        "UPDATE users SET streak_days = 1, last_active_date = ? WHERE telegram_id = ?",
                        (today_str, telegram_id)
                    )
                    await db.commit()
            else:
                await db.execute(
                    "UPDATE users SET last_active_date = ? WHERE telegram_id = ?",
                    (today_str, telegram_id)
                )
                await db.commit()

        return user

async def update_user_activity(telegram_id: int):
    today_str = date.today().isoformat()
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT last_active_date, streak_days FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
            row = await cursor.fetchone()
        if row:
            last_active = row['last_active_date']
            streak = row['streak_days']
            if last_active != today_str:
                if last_active:
                    last_date = date.fromisoformat(last_active)
                    if last_date == date.today() - timedelta(days=1):
                        streak += 1
                    else:
                        streak = 1
                else:
                    streak = 1
                await db.execute(
                    "UPDATE users SET streak_days = ?, last_active_date = ? WHERE telegram_id = ?",
                    (streak, today_str, telegram_id)
                )
                await db.execute(
                    "INSERT OR IGNORE INTO activity_logs (user_id, activity_date) VALUES (?, ?)",
                    (telegram_id, today_str)
                )
                await db.commit()

async def get_user_activity_calendar(telegram_id: int):
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT activity_date FROM activity_logs WHERE user_id = ? ORDER BY activity_date DESC LIMIT 30",
            (telegram_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [row['activity_date'] for row in rows]

async def add_custom_word_for_user(telegram_id: int, eng: str, tr: str):
    async with get_db() as db:
        await db.execute("""
            INSERT INTO words (english_word, translation, part_of_speech, category, is_custom, user_id)
            VALUES (?, ?, 'custom', 'Мои слова', 1, ?)
        """, (eng.strip(), tr.strip(), telegram_id))
        await db.commit()


async def get_user_stats(telegram_id: int):
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        # Всего слов в системе
        async with db.execute("SELECT COUNT(*) as cnt FROM words") as cursor:
            total_words_row = await cursor.fetchone()
            total_words = total_words_row['cnt'] if total_words_row else 1025

        # Выученные слова пользователя
        async with db.execute(
            "SELECT COUNT(*) as cnt FROM user_words WHERE user_id = ? AND status = 'learned'",
            (telegram_id,)
        ) as cursor:
            learned_row = await cursor.fetchone()
            learned_count = learned_row['cnt'] if learned_row else 0

        # Изучаемые слова
        async with db.execute(
            "SELECT COUNT(*) as cnt FROM user_words WHERE user_id = ? AND status = 'learning'",
            (telegram_id,)
        ) as cursor:
            learning_row = await cursor.fetchone()
            learning_count = learning_row['cnt'] if learning_row else 0

        # Данные юзера
        async with db.execute("SELECT streak_days FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
            user_row = await cursor.fetchone()
            streak = user_row['streak_days'] if user_row else 1

        active_count = learned_count + learning_count

        return {
            "total_words": total_words,
            "learned_words": learned_count,
            "learning_words": learning_count,
            "active_words": active_count,
            "remaining_words": max(0, total_words - learned_count),
            "streak_days": streak,
            "weekly_learned": active_count % 50 if active_count % 50 != 0 else (50 if active_count > 0 else 0)
        }


async def get_user_learned_words_list(telegram_id: int):
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT w.english_word, w.translation, w.part_of_speech 
            FROM words w
            JOIN user_words uw ON w.word_id = uw.word_id
            WHERE uw.user_id = ? AND uw.status = 'learned'
            ORDER BY w.word_id DESC
        """, (telegram_id,)) as cursor:
            return await cursor.fetchall()


# ----------------- WORDS & LEARNING -----------------

async def get_user_selected_category(telegram_id: int) -> str:
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT selected_category FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
            row = await cursor.fetchone()
            return row['selected_category'] if row and row['selected_category'] else 'all'

async def set_user_selected_category(telegram_id: int, category: str):
    async with get_db() as db:
        await db.execute("UPDATE users SET selected_category = ? WHERE telegram_id = ?", (category, telegram_id))
        await db.commit()

async def get_next_card_word(telegram_id: int, current_word_id: int = None):
    """
    Возвращает следующее слово для режима карточек с учетом выбранной категории.
    """
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        await db.execute("""
            INSERT OR IGNORE INTO user_words (user_id, word_id, status)
            SELECT ?, word_id, 'new' FROM words
        """, (telegram_id,))
        await db.commit()

        cat = await get_user_selected_category(telegram_id)
        
        where_clause = "WHERE uw.user_id = ? AND uw.status != 'learned'"
        params = [telegram_id]

        if cat != 'all':
            where_clause += " AND w.category = ?"
            params.append(cat)

        if current_word_id:
            where_clause += " AND w.word_id != ?"
            params.append(current_word_id)

        query = f"""
            SELECT w.*, uw.status 
            FROM words w
            JOIN user_words uw ON w.word_id = uw.word_id
            {where_clause}
            ORDER BY CASE uw.status WHEN 'new' THEN 1 WHEN 'learning' THEN 2 END, RANDOM()
            LIMIT 1
        """

        async with db.execute(query, tuple(params)) as cursor:
            return await cursor.fetchone()

async def get_quiz_question(telegram_id: int):
    """
    Возвращает целевое слово и 3 случайных неправильных варианта с учетом выбранной категории.
    """
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        cat = await get_user_selected_category(telegram_id)

        where_clause = "WHERE uw.user_id = ? AND uw.status != 'learned'"
        params = [telegram_id]

        if cat != 'all':
            where_clause += " AND w.category = ?"
            params.append(cat)

        query = f"""
            SELECT w.* 
            FROM words w
            JOIN user_words uw ON w.word_id = uw.word_id
            {where_clause}
            ORDER BY RANDOM()
            LIMIT 1
        """

        async with db.execute(query, tuple(params)) as cursor:
            target_word = await cursor.fetchone()

        if not target_word:
            return None, []

        # Берем 3 случайных других перевода
        async with db.execute("""
            SELECT translation FROM words 
            WHERE word_id != ? 
            ORDER BY RANDOM() 
            LIMIT 3
        """, (target_word['word_id'],)) as cursor:
            options_rows = await cursor.fetchall()

        options = [row['translation'] for row in options_rows]
        options.append(target_word['translation'])
        
        import random
        random.shuffle(options)

        return target_word, options


async def mark_word_as_learned(telegram_id: int, word_id: int):
    async with get_db() as db:
        await db.execute("""
            INSERT INTO user_words (user_id, word_id, status)
            VALUES (?, ?, 'learned')
            ON CONFLICT(user_id, word_id) DO UPDATE SET status = 'learned'
        """, (telegram_id, word_id))
        await db.commit()

async def mark_word_as_learning(telegram_id: int, word_id: int):
    async with get_db() as db:
        await db.execute("""
            INSERT INTO user_words (user_id, word_id, status)
            VALUES (?, ?, 'learning')
            ON CONFLICT(user_id, word_id) DO UPDATE SET status = 'learning'
        """, (telegram_id, word_id))
        await db.commit()


async def set_user_reminder_hour(telegram_id: int, hour: int):
    async with get_db() as db:
        await db.execute("UPDATE users SET reminder_hour = ? WHERE telegram_id = ?", (hour, telegram_id))
        await db.commit()

async def get_user_reminder_hour(telegram_id: int) -> int:
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT reminder_hour FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
            row = await cursor.fetchone()
            return row['reminder_hour'] if row and row['reminder_hour'] is not None else 9

async def get_users_for_reminder_hour(hour: int):
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT telegram_id FROM users WHERE reminder_hour = ?", (hour,)) as cursor:
            rows = await cursor.fetchall()
            return [row['telegram_id'] for row in rows]

async def get_categories_stats():
    icons = {
        "Общие слова": "🔤",
        "Путешествия": "✈️",
        "IT и Технологии": "💻",
        "Еда и Ресторан": "🍕",
        "Бизнес и Работа": "💼",
        "Природа и Город": "🌿",
        "Разговорный сленг": "🗣️",
        "Комплименты": "💖",
        "Ругательства": "🤬",
        "Продвинутый C1": "🎓",
        "Мои слова": "⭐"
    }



    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT category, COUNT(*) as cnt FROM words GROUP BY category") as cursor:
            rows = await cursor.fetchall()
            res = []
            for row in rows:
                cat_name = row['category'] if row['category'] else 'Общие слова'
                res.append({
                    "name": cat_name,
                    "count": row['cnt'],
                    "icon": icons.get(cat_name, "📚")
                })
            return res




