from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
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


router = Router()


def make_progress_bar(percentage: float, length: int = 10) -> str:
    filled_length = int(round(length * percentage / 100))
    bar = '█' * filled_length + '░' * (length - filled_length)
    return bar

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
    await call.message.edit_text(welcome_text, parse_mode="HTML", reply_markup=get_main_menu_keyboard())
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

@router.message(F.text)
async def handle_user_custom_word_text(message: Message):
    user_id = message.from_user.id
    if user_id in user_adding_words:
        text = message.text
        if "-" in text or "=" in text:
            delimiter = "-" if "-" in text else "="
            parts = text.split(delimiter, 1)
            eng = parts[0].strip()
            tr = parts[1].strip()
            if eng and tr:
                from database.models import add_custom_word_for_user
                await add_custom_word_for_user(user_id, eng, tr)
                user_adding_words.remove(user_id)
                await message.answer(
                    f"✅ Слово <b>{eng.capitalize()}</b> — <i>{tr}</i> успешно добавлено в <b>⭐ Мои слова</b>!",
                    parse_mode="HTML",
                    reply_markup=get_main_menu_keyboard()
                )
                return
        await message.answer("❌ Неверный формат. Пожалуйста, отправь в виде: <code>apple - яблоко</code>", parse_mode="HTML")



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

