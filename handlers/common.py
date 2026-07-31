import os
import aiosqlite
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart


from database.models import get_or_create_user, get_user_stats, update_user_activity, get_user_reminder_hour, set_user_reminder_hour, get_categories_stats, get_user_selected_category, set_user_selected_category, get_user_learned_words_list, get_user_activity_calendar
from keyboards.inline import get_main_menu_keyboard, get_back_to_menu_keyboard, get_reminder_settings_keyboard, get_categories_keyboard, get_stats_keyboard, get_back_to_stats_keyboard



router = Router()


@router.callback_query(F.data == "categories_menu")
async def cb_categories_menu(call: CallbackQuery):
    user_id = call.from_user.id
    categories = await get_categories_stats()
    selected = await get_user_selected_category(user_id)
    text = (
        f"📚 <b>Выбор темы для изучения</b>\n\n"
        f"Выбери интересующую категорию слов. Бот будет выдавать карточки и викторины только по выбранной теме!"
    )
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_categories_keyboard(categories, selected))
    await call.answer()

@router.callback_query(F.data.startswith("set_category_"))
async def cb_set_category(call: CallbackQuery):
    user_id = call.from_user.id
    category_name = call.data.replace("set_category_", "")
    await set_user_selected_category(user_id, category_name)
    
    categories = await get_categories_stats()
    label_show = "Все слова" if category_name == "all" else category_name
    await call.answer(f"✅ Выбрана тема: {label_show}!", show_alert=True)

    text = (
        f"📚 <b>Выбор темы для изучения</b>\n\n"
        f"Текущая тема: <b>{label_show}</b>.\n"
        f"Выбери интересующую категорию слов. Бот будет выдавать карточки и викторины только по выбранной теме!"
    )
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_categories_keyboard(categories, category_name))



def make_progress_bar(percentage: float, length: int = 10) -> str:
    filled_length = int(round(length * percentage / 100))
    bar = '█' * filled_length + '░' * (length - filled_length)
    return bar

async def run_update_task(status_msg: Message):
    import asyncio
    import sys
    try:
        proc_git = await asyncio.create_subprocess_shell(
            "git pull origin main",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=os.getcwd()
        )
        stdout_git, stderr_git = await proc_git.communicate()
        output_text = stdout_git.decode().strip() if stdout_git else stderr_git.decode().strip()

        await status_msg.edit_text(
            "🚀 <b>СЛУЖБА ОБНОВЛЕНИЯ БОТА</b>\n\n"
            "✅ <i>1/2 Исходный код с GitHub получен!</i>\n"
            "⏳ <i>2/2 Синхронизируем базу данных словаря...</i>",
            parse_mode="HTML"
        )

        python_exec = sys.executable or "python3"
        proc_seed = await asyncio.create_subprocess_shell(
            f"{python_exec} seed_words.py",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=os.getcwd()
        )
        stdout_seed, _ = await proc_seed.communicate()
        seed_text = stdout_seed.decode().strip() if stdout_seed else "База данных актуальна."

        res_text = (
            f"🎉 <b>ОБНОВЛЕНИЕ БОТА УСПЕШНО ЗАВЕРШЕНО!</b>\n\n"
            f"📥 <b>Статус Git Pull:</b>\n"
            f"<code>{output_text}</code>\n\n"
            f"🔤 <b>Статус Синхронизации БД:</b>\n"
            f"<code>{seed_text}</code>\n\n"
            f"✨ <i>Все свежие доработки применены! Перезапустите бота.</i>"
        )
        await status_msg.edit_text(res_text, parse_mode="HTML", reply_markup=get_main_menu_keyboard())
    except Exception as e:
        await status_msg.edit_text(f"❌ <b>Ошибка при авто-обновлении:</b>\n<code>{e}</code>", parse_mode="HTML")

@router.message(Command("update_bot"))
async def cmd_update_bot(message: Message):
    import asyncio
    status_msg = await message.answer(
        "🚀 <b>СЛУЖБА ОБНОВЛЕНИЯ БОТА ЗАПУЩЕНА</b>\n\n"
        "⏳ <i>1/2 Связываемся с репозиторием GitHub (git pull origin main)...</i>",
        parse_mode="HTML"
    )
    asyncio.create_task(run_update_task(status_msg))







@router.message(CommandStart())
async def cmd_start(message: Message):

    user_id = message.from_user.id
    first_name = message.from_user.first_name
    await get_or_create_user(user_id)
    
    welcome_text = (
        f"👋 <b>Привет, {first_name}!</b>\n\n"
        f"Добро пожаловать в тренажер <b>1025 самых популярных английских слов</b>!\n\n"
        f"🎯 <b>Целевой темп:</b> 50 слов в неделю (~7 слов в день).\n"
        f"🔥 <b>Страйк:</b> Бот фиксирует твои ежедневные занятия.\n"
        f"🧠 <b>Алгоритм SM-2:</b> Интервальное повторение слов.\n\n"
        f"Выбери режим обучения ниже, чтобы начать! 👇"
    )
    await message.answer(welcome_text, parse_mode="HTML", reply_markup=get_main_menu_keyboard())

@router.callback_query(F.data == "main_menu")
async def cb_main_menu(call: CallbackQuery):
    await update_user_activity(call.from_user.id)
    welcome_text = (
        f"🏠 <b>Главное меню</b>\n\n"
        f"Готов продолжить обучение? Выбери нужный раздел:"
    )
    try:
        await call.message.edit_text(welcome_text, parse_mode="HTML", reply_markup=get_main_menu_keyboard())
    except Exception:
        await call.message.delete()
        await call.message.answer(welcome_text, parse_mode="HTML", reply_markup=get_main_menu_keyboard())
    await call.answer()


@router.callback_query(F.data == "settings_menu")
async def cb_settings_menu(call: CallbackQuery):
    user_id = call.from_user.id
    current_hour = await get_user_reminder_hour(user_id)
    text = (
        f"⚙️ <b>Настройки ежедневных напоминаний</b>\n\n"
        f"Текущее время рассылки: <b>{current_hour}:00</b> (по UTC).\n"
        f"Выбери удобный час, когда бот будет приглашать тебя на проверку слов:"
    )
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_reminder_settings_keyboard(current_hour))
    await call.answer()

@router.callback_query(F.data.startswith("set_reminder_"))
async def cb_set_reminder(call: CallbackQuery):
    user_id = call.from_user.id
    hour = int(call.data.split("_")[2])
    await set_user_reminder_hour(user_id, hour)
    await call.answer(f"✅ Напоминания установлены на {hour}:00!", show_alert=True)
    text = (
        f"⚙️ <b>Настройки ежедневных напоминаний</b>\n\n"
        f"Текущее время рассылки: <b>{hour}:00</b> (по UTC).\n"
        f"Выбери удобный час, когда бот будет приглашать тебя на проверку слов:"
    )
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_reminder_settings_keyboard(hour))

@router.callback_query(F.data == "my_stats")
async def cb_stats(call: CallbackQuery):
    user_id = call.from_user.id
    stats = await get_user_stats(user_id)
    activity_dates = await get_user_activity_calendar(user_id)
    
    total = stats['total_words']
    learned = stats['learned_words']
    learning = stats['learning_words']
    remaining = stats['remaining_words']
    streak = stats['streak_days']
    weekly = stats['weekly_learned']
    
    overall_percent = (learned / total) * 100 if total > 0 else 0
    weekly_percent = (weekly / 50) * 100
    
    overall_bar = make_progress_bar(overall_percent)
    weekly_bar = make_progress_bar(weekly_percent)

    # Календарь за последние 7 дней (Heatmap)
    from datetime import date, timedelta
    calendar_squares = []
    for i in range(6, -1, -1):
        d_str = (date.today() - timedelta(days=i)).isoformat()
        if d_str in activity_dates:
            calendar_squares.append("🟩")
        else:
            calendar_squares.append("⬜")
    calendar_str = " ".join(calendar_squares)

    stats_text = (
        f"📊 <b>Ваш профиль и статистика</b>\n\n"
        f"🔥 <b>Страйк:</b> <code>{streak}</code> { 'день' if streak == 1 else 'дней' } подряд в боте!\n"
        f"📅 <b>Активность за неделю:</b> {calendar_str}\n\n"
        f"📈 <b>Недельный прогресс (Пак из 50 слов):</b>\n"
        f"<code>[{weekly_bar}]</code> {weekly}/50 слов (включая изучаемые)\n\n"
        f"🎓 <b>Общий прогресс выученного:</b>\n"
        f"<code>[{overall_bar}]</code> {overall_percent:.1f}%\n\n"
        f"✅ <b>Полностью выучено:</b> {learned} слов\n"
        f"🧠 <b>В процессе изучения:</b> {learning} слов\n"
        f"⏳ <b>Не изучено:</b> {remaining} слов\n"
        f"📚 <b>Всего в словаре:</b> {total} слов"
    )
    await call.message.edit_text(stats_text, parse_mode="HTML", reply_markup=get_stats_keyboard())
    await call.answer()

# Хранилище диалогов добавления слов
user_adding_words = set()

@router.callback_query(F.data == "add_custom_word")
async def cb_add_custom_word(call: CallbackQuery):
    user_id = call.from_user.id
    user_adding_words.add(user_id)
    text = (
        f"➕ <b>Добавление собственного слова в словарь</b>\n\n"
        f"Пришли слово и перевод в формате:\n"
        f"<code>apple - яблоко</code> или <code>freedom = свобода</code>\n\n"
        f"Оно моментально появится в категории <b>⭐ Мои слова</b>!"
    )
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_back_to_menu_keyboard())
    await call.answer()


# ----------------- РЕЖИМ СПРИНТ (60 SECONDS BLITZ) -----------------
sprint_scores = {}

async def send_sprint_question(call: CallbackQuery):
    user_id = call.from_user.id
    import random
    from database.db import get_db
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT english_word, translation FROM words ORDER BY RANDOM() LIMIT 2") as cursor:
            rows = await cursor.fetchall()

    if len(rows) < 2:
        return

    is_correct_pair = random.choice([True, False])
    target_word = rows[0]['english_word'].capitalize()
    
    if is_correct_pair:
        shown_translation = rows[0]['translation']
    else:
        shown_translation = rows[1]['translation']

    score_data = sprint_scores.get(user_id, {"score": 0, "count": 0})
    score = score_data["score"]
    count = score_data["count"]

    text = (
        f"⚡ <b>РЕЖИМ СПРИНТ (60 Секунд)</b>\n\n"
        f"🏆 Набрано очков: <b>{score}</b> / Ответов: <b>{count}</b>\n\n"
        f"Слово: <b>{target_word}</b>\n"
        f"Перевод: <b>{shown_translation}</b>\n\n"
        f"<i>Правильный ли перевод представлен выше?</i>"
    )
    from keyboards.inline import get_sprint_keyboard
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_sprint_keyboard(is_correct_pair))

@router.callback_query(F.data == "mode_sprint")
async def cb_mode_sprint(call: CallbackQuery):
    user_id = call.from_user.id
    sprint_scores[user_id] = {"score": 0, "count": 0}
    await send_sprint_question(call)
    await call.answer("⚡ Спринт запущен! Набирай рекорд!")

@router.callback_query(F.data.startswith("sprint_ans_"))
async def cb_sprint_answer(call: CallbackQuery):
    user_id = call.from_user.id
    parts = call.data.split("_")
    user_choice_true = parts[2] == "true"
    is_actual_pair_true = parts[3] == "1"

    score_data = sprint_scores.get(user_id, {"score": 0, "count": 0})
    score_data["count"] += 1

    if user_choice_true == is_actual_pair_true:
        score_data["score"] += 10
        await call.answer("✅ ВЕРНО! +10 XP")
    else:
        await call.answer("❌ НЕВЕРНО!")

    sprint_scores[user_id] = score_data
    await send_sprint_question(call)

# ----------------- РЕЖИМ КАДР И ЦИТАТЫ ИЗ СЕРИАЛОВ -----------------
@router.callback_query(F.data == "mode_movie_quote")
async def cb_mode_movie_quote(call: CallbackQuery):
    user_id = call.from_user.id
    import random

    videos_base_dir = os.path.join(os.getcwd(), "assets", "videos")
    all_local_videos = []

    if os.path.exists(videos_base_dir):
        for root, dirs, files in os.walk(videos_base_dir):
            for file in files:
                if file.lower().endswith(('.mp4', '.mov', '.mkv')) and not file.startswith('.'):
                    all_local_videos.append(os.path.join(root, file))

    if not all_local_videos:
        await call.answer("Локальные видеоролики загружаются на сервер...", show_alert=True)
        return

    chosen_video_path = random.choice(all_local_videos)
    series_name = os.path.basename(os.path.dirname(chosen_video_path))
    raw_name = os.path.splitext(os.path.basename(chosen_video_path))[0]

    # Авто-поиск перевода в базе данных по сходству или дефолтный словарь
    translation_text = None
    from database.db import get_db
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT translation FROM words WHERE LOWER(english_word) LIKE ? OR LOWER(example_sentence) LIKE ?", 
                              (f"%{raw_name.lower()}%", f"%{raw_name.lower()}%")) as cursor:
            row = await cursor.fetchone()
            if row:
                translation_text = row['translation']

    # Известные переводы
    translations_dict = {
        "go fuck yourself": "Пошел нахуй!",
        "alright, i give up, what then?": "Ладно, я сдаюсь, и что дальше?",
        "anybody around here love the word \"jimmy choo shoes\"?": "Кто-нибудь здесь любит словосочетание «туфли Jimmy Choo»?",
        "i give him up, we can give the whole fucking thing up.": "Если я сдам его, мы можем нахрен сворачивать всё наше дело.",
        "stop getting cunty": "Перестань выпендриваться / стервозничать.",
        "what's his name again?": "Как его там снова зовут?",
        "only you can get them for us.": "Только ты можешь достать их для нас.",
        "- so what? - \"so what\"?": "- Ну и что? - «Ну и что»?!",
        "and i... i think about you all the time.": "И я... я думал о тебе всё это время.",
        "heisenberg, come on, break it out.": "Хайзенберг, давай же, выкатывай это.",
        "hey, come on. what, you gonna argue?": "Эй, давай. Что, спорить будешь?",
        "i don't know, how about taco cabeza?": "Я не знаю, как насчет Тако Кабеса?",
        "listen, old man, talk is talk.": "Слушай, старик, разговоры разговорчиками.",
        "nice and public. open 24 hours.": "Хорошо и публично. Открыто 24 часа.",
        "of never once believing in yourself?": "О том, чтобы ни разу в себя не поверить?",
        "okay. you got me there.": "Ладно. Здесь ты меня умыл.",
        "seventeen and a half. minus the half for wasting my time.": "Семнадцать с половиной. Минус пол-пакета за то, что потратил мое время.",
        "so you do have a plan.": "Значит, план у тебя все-таки есть.",
        "what did you say?": "Что ты сказал?",
        "what, they close the mall or something?": "Что, торговый центр закрылся или типа того?",
        "you got something to say?": "Тебе есть что сказать?",
        "you told me 2 pounds,": "Ты сказал мне 2 фунта,",
        "in his car, not in the school.": "В его машине, а не в школе.",
        "we just can't say for sure.": "Мы просто не можем утверждать наверняка."
    }

    if not translation_text:
        cleaned_key = raw_name.lower().strip().rstrip(".")
        translation_text = translations_dict.get(cleaned_key, "Разговорная фраза из сериала")

    caption = (
        f"🎬 <b>КАДР ИЗ СЕРИАЛА ({series_name})</b>\n\n"
        f"💬 <b>Фраза / Цитата:</b>\n"
        f"<i>\"{raw_name}\"</i>\n\n"
        f"🇷🇺 <b>Перевод:</b>\n"
        f"<b>{translation_text}</b>"
    )
    from aiogram.types import FSInputFile
    from keyboards.inline import get_movie_quote_keyboard
    video_file = FSInputFile(chosen_video_path)
    try:
        await call.message.answer_video(video=video_file, caption=caption, parse_mode="HTML", reply_markup=get_movie_quote_keyboard(), request_timeout=60)
    except Exception as err:
        # В случае сетевых сбоев серверов Telegram
        await call.message.answer(f"🎬 <b>КАДР ИЗ СЕРИАЛА ({series_name})</b>\n\n💬 <b>Фраза / Цитата:</b>\n<i>\"{raw_name}\"</i>\n\n🇷🇺 <b>Перевод:</b>\n<b>{translation_text}</b>", parse_mode="HTML", reply_markup=get_movie_quote_keyboard())
    await call.answer()



@router.callback_query(F.data == "movie_know_word")
async def cb_movie_know_word(call: CallbackQuery):
    user_id = call.from_user.id
    # Получаем последнее слово цитаты для фиксации его как выученное
    from database.db import get_db
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT word_id FROM words WHERE category = 'Цитаты из сериалов' ORDER BY RANDOM() LIMIT 1") as cursor:
            row = await cursor.fetchone()
            if row:
                from database.models import mark_word_as_learned
                await mark_word_as_learned(user_id, row['word_id'])

    await call.answer("⭐ Кадр/Фраза отправлена в выученные!", show_alert=True)
    await cb_mode_movie_quote(call)

user_checking_movie_quote = {}

@router.callback_query(F.data == "review_learned_movie_quotes")
async def cb_review_learned_movie_quotes(call: CallbackQuery):
    user_id = call.from_user.id
    from database.models import get_user_learned_movie_quotes
    quotes = await get_user_learned_movie_quotes(user_id)

    if not quotes:
        await call.answer("У вас пока нет выученных кадров для проверки! Сначала отметьте кадры кнопкой 'Уже знаю'.", show_alert=True)
        return

    import random
    quote = random.choice(quotes)
    user_checking_movie_quote[user_id] = quote

    text = (
        f"✍️ <b>ПРОВЕРКА ВЫУЧЕННОГО КАДРА ИЗ СЕРИАЛА</b>\n\n"
        f"💬 <b>Контекст / Сцена:</b>\n"
        f"<i>{quote['example_sentence']}</i>\n\n"
        f"<b>Напишите эту фразу на английском языке в чат:</b>\n"
        f"<i>(Если сложно вспомнить — нажмите «💡 Подсказка» ниже)</i>"
    )
    from keyboards.inline import get_movie_quote_review_keyboard
    await call.message.answer(text, parse_mode="HTML", reply_markup=get_movie_quote_review_keyboard())
    await call.answer()

@router.callback_query(F.data == "movie_quote_hint")
async def cb_movie_quote_hint(call: CallbackQuery):
    user_id = call.from_user.id
    quote = user_checking_movie_quote.get(user_id)

    if not quote:
        await call.answer("Загрузите новую фразу для проверки...", show_alert=True)
        return

    await call.answer(f"💡 Перевод: {quote['translation']}", show_alert=True)




@router.callback_query(F.data == "my_learned_movie_quotes")
async def cb_my_learned_movie_quotes(call: CallbackQuery):
    user_id = call.from_user.id
    from database.models import get_user_learned_movie_quotes
    quotes = await get_user_learned_movie_quotes(user_id)

    if not quotes:
        text = (
            f"🎬 <b>Выученные фразы из сериалов</b>\n\n"
            f"У вас пока нет выученных кадров из сериалов!\n"
            f"В режиме <b>«🎬 Кадр из сериала»</b> нажимайте <i>«✅ Уже знаю»</i>, чтобы сохранять их сюда."
        )
    else:
        list_items = []
        for q in quotes[:30]:
            list_items.append(f"• <b>{q['english_word'].capitalize()}</b> — {q['translation']}\n  <i>{q['example_sentence']}</i>")
        
        list_str = "\n\n".join(list_items)
        text = (
            f"🎬 <b>Ваши выученные фразы из сериалов ({len(quotes)}):</b>\n\n"
            f"{list_str}"
        )

    await call.message.answer(text, parse_mode="HTML", reply_markup=get_back_to_stats_keyboard())
    await call.answer()








user_searching_words = set()

@router.callback_query(F.data == "search_word_prompt")
async def cb_search_word_prompt(call: CallbackQuery):
    user_id = call.from_user.id
    user_searching_words.add(user_id)
    text = (
        f"🔍 <b>Поиск слова в словаре</b>\n\n"
        f"Отправьте мне любое английское или русское слово (например, <code>freedom</code> или <code>свобода</code>).\n"
        f"Я мгновенно найду его в базе, покажу перевод, примеры и контексты!"
    )
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_back_to_menu_keyboard())
    await call.answer()

@router.callback_query(F.data == "weak_words_list")
async def cb_weak_words_list(call: CallbackQuery):
    user_id = call.from_user.id
    from database.db import get_db
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT w.english_word, w.translation, uw.repetition_count 
            FROM user_words uw 
            JOIN words w ON uw.word_id = w.word_id 
            WHERE uw.user_id = ? AND uw.status = 'learning'
            ORDER BY uw.repetition_count ASC LIMIT 10
        """, (user_id,)) as cursor:
            rows = await cursor.fetchall()

    if not rows:
        text = (
            f"⚠️ <b>Ваши трудные слова</b>\n\n"
            f"У вас пока нет проблемных слов! Продолжайте проходить карточки и викторины."
        )
    else:
        list_str = "\n".join([f"• <b>{r['english_word'].capitalize()}</b> — {r['translation']}" for r in rows])
        text = (
            f"⚠️ <b>Ваши трудные слова (требуют повторения):</b>\n\n"
            f"{list_str}\n\n"
            f"<i>Рекомендуем пройти викторину или карточки для их закрепления!</i>"
        )

    await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_back_to_menu_keyboard())
    await call.answer()


@router.message(F.text)
async def handle_user_custom_word_text(message: Message):
    user_id = message.from_user.id

    # Проверка выученного кадра из сериала
    if user_id in user_checking_movie_quote:
        quote = user_checking_movie_quote.pop(user_id)
        user_input = message.text.strip().lower()
        target_text = quote['english_word'].strip().lower()

        import re
        from difflib import SequenceMatcher

        # Очистка от любой пунктуации и знаков препинания
        clean_input = re.sub(r'[^\w\s]', '', user_input)
        clean_target = re.sub(r'[^\w\s]', '', target_text)

        # Вычисление схожести текстов (допуск опечаток до 75% совпадения)
        similarity = SequenceMatcher(None, clean_input, clean_target).ratio()

        if clean_input == clean_target or similarity >= 0.75:
            text = (
                f"🎉 <b>Блестяще! Вы правильно вспомнили фразу!</b>\n\n"
                f"🔤 Оригинал: <b>{quote['english_word'].capitalize()}</b>\n"
                f"🇷🇺 Перевод: <b>{quote['translation']}</b>\n"
                f"💬 Реплика: <i>{quote['example_sentence']}</i>\n\n"
                f"<i>(Совпадение: {int(similarity * 100)}%, опечатки и знаки препинания мягко прощены)</i>"
            )
        else:
            text = (
                f"💡 <b>Почти получилось!</b>\n\n"
                f"Ваш ответ: <i>{message.text}</i>\n"
                f"Правильная фраза: <b>{quote['english_word'].capitalize()}</b>\n"
                f"🇷🇺 Перевод: <b>{quote['translation']}</b>\n\n"
                f"<i>Не переживайте, тренируйтесь чаще!</i>"
            )

        from keyboards.inline import get_movie_quote_keyboard
        await message.answer(text, parse_mode="HTML", reply_markup=get_movie_quote_keyboard())
        return

    if user_id in user_searching_words:
        user_searching_words.remove(user_id)
        query = message.text.strip().lower()
        from database.db import get_db
        async with get_db() as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM words WHERE LOWER(english_word) LIKE ? OR LOWER(translation) LIKE ? LIMIT 1", (f"%{query}%", f"%{query}%")) as cursor:
                word = await cursor.fetchone()

        if word:
            res_text = (
                f"🔍 <b>Результат поиска по запросу '{query}':</b>\n\n"
                f"🔤 <b>{word['english_word'].capitalize()}</b> — <i>{word['translation']}</i>\n"
                f"📚 Категория: <b>{word['category']}</b>\n\n"
                f"💬 Пример: <i>{word['example_sentence']}</i>\n\n"
                f"{word['context_examples'] if word['context_examples'] else ''}"
            )
        else:
            res_text = f"❌ К сожалению, слово <b>'{query}'</b> не найдено в базе бота."

        await message.answer(res_text, parse_mode="HTML", reply_markup=get_main_menu_keyboard())
        return

    if user_id in user_adding_words:
        raw_input = message.text.strip()
        import re
        # Гибкое разбиение по любым знакам препинания: -, =, :, ➔, двоеточия или двойным пробелам
        parts = re.split(r'[-=:\t—–➔]+', raw_input, maxsplit=1)
        if len(parts) < 2:
            # Если нет знака препинания, делим по первому русскому слову или пробелу
            parts = re.split(r'\s+(?=[а-яА-ЯёЁ])', raw_input, maxsplit=1)

        if len(parts) >= 2:
            eng = parts[0].strip()
            tr = parts[1].strip()
            # Очищаем от случайных лишних знаков
            eng = re.sub(r'[^a-zA-Z\s\'-]', '', eng)
            if eng and tr:
                from database.models import add_custom_word_for_user
                await add_custom_word_for_user(user_id, eng, tr)
                user_adding_words.remove(user_id)
                await message.answer(
                    f"✅ Слово <b>{eng.capitalize()}</b> — <i>{tr}</i> успешно добавлено в <b>⭐ Мои слова</b>!\n"
                    f"<i>(Орфография и пунктуация мягко распознаны)</i>",
                    parse_mode="HTML",
                    reply_markup=get_main_menu_keyboard()
                )
                return

        await message.answer("💡 Отправь слово и перевод в любом удобном виде, например: <code>apple яблоко</code> или <code>apple - яблоко</code>", parse_mode="HTML")





@router.callback_query(F.data == "my_learned_words")
async def cb_my_learned_words(call: CallbackQuery):
    user_id = call.from_user.id
    learned_words = await get_user_learned_words_list(user_id)

    if not learned_words:
        await call.message.edit_text(
            "📖 <b>Ваш список выученных слов</b>\n\n"
            "Вы еще не поместили ни одного слова в выученные. Нажмите <i>«Уже знаю это слово»</i> или пройдите 5 этапов SM-2 карточек!",
            parse_mode="HTML",
            reply_markup=get_back_to_stats_keyboard()
        )
        await call.answer()
        return

    words_text = "\n".join([f"• <b>{row['english_word'].capitalize()}</b> — {row['translation']} <i>({row['part_of_speech']})</i>" for row in learned_words[:50]])
    
    more_note = f"\n\n<i>...и еще {len(learned_words) - 50} слов</i>" if len(learned_words) > 50 else ""

    text = (
        f"📖 <b>Ваш список выученных слов ({len(learned_words)}):</b>\n\n"
        f"{words_text}"
        f"{more_note}"
    )
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_back_to_stats_keyboard())
    await call.answer()

@router.callback_query(F.data == "download_learned_pdf")
async def cb_download_learned_pdf(call: CallbackQuery):
    user_id = call.from_user.id
    first_name = call.from_user.first_name
    learned_words = await get_user_learned_words_list(user_id)

    if not learned_words:
        await call.answer("У вас пока нет выученных слов для скачивания!", show_alert=True)
        return

    await call.answer("⏳ Генерируем красивый PDF документ...")
    import tempfile
    from aiogram.types import FSInputFile
    from services.pdf_generator import generate_learned_words_pdf

    temp_pdf_path = os.path.join(tempfile.gettempdir(), f"learned_words_{user_id}.pdf")
    generate_learned_words_pdf(first_name, learned_words, temp_pdf_path)

    pdf_file = FSInputFile(temp_pdf_path, filename=f"My_English_Vocabulary_{first_name}.pdf")

    caption = (
        f"📑 <b>Ваш личный словарь готовых слов!</b>\n\n"
        f"👤 Ученик: <b>{first_name}</b>\n"
        f"✅ Выучено слов: <b>{len(learned_words)}</b>\n\n"
        f"Файл отлично подходит для распечатки или повторения offline! 🎓"
    )
    await call.message.answer_document(document=pdf_file, caption=caption, parse_mode="HTML")

    if os.path.exists(temp_pdf_path):
        os.remove(temp_pdf_path)



@router.callback_query(F.data == "help_info")
async def cb_help(call: CallbackQuery):
    help_text = (
        f"📖 <b>Как пользоваться ботом?</b>\n\n"
        f"1️⃣ <b>Флеш-карточки:</b> Показывается английское слово. Нажмите <i>«Перевернуть карточку»</i> и оцените сложность (Трудно, Норм, Легко).\n"
        f"2️⃣ <b>Алгоритм SM-2:</b> Чем лучше вы помните слово, тем реже бот будет его повторять.\n"
        f"3️⃣ <b>Викторина:</b> Выберите правильный перевод из 4 вариантов.\n"
        f"4️⃣ <b>«Уже знаю это слово»:</b> Мгновенно исключает слово из проверок.\n"
        f"5️⃣ <b>Настройки:</b> Выберите удобный час для ежедневных напоминаний."
    )
    await call.message.edit_text(help_text, parse_mode="HTML", reply_markup=get_back_to_menu_keyboard())
    await call.answer()

