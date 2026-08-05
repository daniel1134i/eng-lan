import aiosqlite
from aiogram import Router, F
from aiogram.types import CallbackQuery

from database.models import get_next_card_word, mark_word_as_learned, mark_word_as_learning, update_user_activity, get_user_stats
from keyboards.inline import get_card_keyboard, get_back_to_menu_keyboard


router = Router()

async def send_next_card(call: CallbackQuery, current_word_id: int = None):
    user_id = call.from_user.id
    word = await get_next_card_word(user_id, current_word_id=current_word_id)
    stats = await get_user_stats(user_id)

    if not word:
        total = stats['total_words']
        from database.models import get_pack_info
        words_added, pack_start = await get_pack_info(user_id)
        if words_added >= 50:
            from keyboards.inline import get_reset_pack_keyboard
            await call.message.edit_text(
                "🎉 <b>Вы выучили недельный пак слов (50/50)!</b>\n\n"
                "Бот выдает новые слова только через 7 дней от начала изучения пака, чтобы вы успели их надежно закрепить.\n"
                "Если вы уверены, что уже всё запомнили и хотите набрать следующий пак прямо сейчас, нажмите кнопку ниже.",
                parse_mode="HTML",
                reply_markup=get_reset_pack_keyboard()
            )
        else:
            await call.message.edit_text(
                f"🎉 <b>Поздравляем!</b>\nВы выучили все {total} слов в нашем тренажере!",
                parse_mode="HTML",
                reply_markup=get_back_to_menu_keyboard()
            )
        return

    learned = stats['learned_words']
    total = stats['total_words']
    pct = (learned / total * 100) if total > 0 else 0

    text = (
        f"🎴 <b>Флеш-карточка</b>  📊 <code>{learned}/{total} ({pct:.1f}%)</code>\n\n"
        f"🔤 Слово: <b>{word['english_word'].capitalize()}</b>\n"
        f"🏷️ Часть речи: <i>{word['part_of_speech']}</i>\n\n"
        f"💡 <i>Вспомни перевод и нажми кнопку ниже!</i>"
    )
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_card_keyboard(word['word_id'], is_flipped=False))

@router.callback_query(F.data == "mode_cards")
@router.callback_query(F.data == "next_card")
@router.callback_query(F.data.startswith("next_card_"))
async def cb_mode_cards(call: CallbackQuery):
    await update_user_activity(call.from_user.id)
    current_word_id = None
    if call.data.startswith("next_card_"):
        current_word_id = int(call.data.split("_")[2])
    await send_next_card(call, current_word_id=current_word_id)
    await call.answer()

@router.callback_query(F.data.startswith("flip_card_"))
async def cb_flip_card(call: CallbackQuery):
    word_id = int(call.data.split("_")[2])
    user_id = call.from_user.id

    await mark_word_as_learning(user_id, word_id)
    stats = await get_user_stats(user_id)

    from database.db import get_db
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM words WHERE word_id = ?", (word_id,)) as cursor:
            word = await cursor.fetchone()

    if not word:
        await call.answer("Слово не найдено", show_alert=True)
        return

    learned = stats['learned_words']
    total = stats['total_words']
    pct = (learned / total * 100) if total > 0 else 0

    example_str = f"\n\n💬 <b>Пример:</b>\n<i>{word['example_sentence']}</i>" if word['example_sentence'] else ""

    text = (
        f"🎴 <b>Флеш-карточка (Перевернута)</b>  📊 <code>{learned}/{total} ({pct:.1f}%)</code>\n\n"
        f"🔤 Слово: <b>{word['english_word'].capitalize()}</b>\n"
        f"🇷🇺 Перевод: <b>{word['translation']}</b>\n"
        f"🏷️ Часть речи: <i>{word['part_of_speech']}</i>"
        f"{example_str}"
    )
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_card_keyboard(word_id, is_flipped=True))
    await call.answer()

@router.callback_query(F.data.startswith("show_contexts_"))
async def cb_show_contexts(call: CallbackQuery):
    word_id = int(call.data.split("_")[2])
    from database.db import get_db
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT context_examples, english_word FROM words WHERE word_id = ?", (word_id,)) as cursor:
            row = await cursor.fetchone()
    
    ctx = row['context_examples'] if row and row['context_examples'] else "Контексты подгружаются..."
    eng = row['english_word'].capitalize() if row else ""
    await call.answer()
    await call.message.answer(f"💬 <b>Примеры контекстов для '{eng}':</b>\n\n{ctx}", parse_mode="HTML")

@router.callback_query(F.data.startswith("show_synonyms_"))
async def cb_show_synonyms(call: CallbackQuery):
    word_id = int(call.data.split("_")[2])
    from database.db import get_db
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT synonyms, english_word FROM words WHERE word_id = ?", (word_id,)) as cursor:
            row = await cursor.fetchone()
    
    syn = row['synonyms'] if row and row['synonyms'] else "Инсайты подгружаются..."
    eng = row['english_word'].capitalize() if row else ""
    await call.answer()
    await call.message.answer(f"💡 <b>Синонимы и тонкости слова '{eng}':</b>\n\n{syn}", parse_mode="HTML")


@router.callback_query(F.data.startswith("know_word_"))
async def cb_know_word(call: CallbackQuery):
    if call.data.startswith("know_word_quiz_"):
        word_id = int(call.data.split("_")[3])
    else:
        word_id = int(call.data.split("_")[2])

    user_id = call.from_user.id
    await mark_word_as_learned(user_id, word_id)
    
    await call.answer("✅ Слово помечено как выученное!", show_alert=True)
    await send_next_card(call, current_word_id=word_id)


