from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.models import get_quiz_question, mark_word_as_learning, update_user_activity, get_user_stats

from keyboards.inline import get_quiz_keyboard, get_back_to_menu_keyboard

router = Router()



# Временное хранилище правильных ответов активных викторин
active_quizzes = {}

async def send_next_quiz(call: CallbackQuery):
    user_id = call.from_user.id
    word, options = await get_quiz_question(user_id)
    stats = await get_user_stats(user_id)

    if not word or not options:
        await call.message.edit_text(
            "🎉 <b>Поздравляем!</b>\nВы выучили все 1025 слов!",
            parse_mode="HTML",
            reply_markup=get_back_to_menu_keyboard()
        )
        return

    word_id = word['word_id']
    active_quizzes[f"{user_id}_{word_id}"] = {
        "correct": word['translation'],
        "options": options
    }

    learned = stats['learned_words']
    total = stats['total_words']
    pct = (learned / total * 100) if total > 0 else 0

    text = (
        f"🧩 <b>Викторина</b>  📊 <code>{learned}/{total} ({pct:.1f}%)</code>\n\n"
        f"Как переводится слово: <b>{word['english_word'].capitalize()}</b>?\n"
        f"<i>Часть речи: {word['part_of_speech']}</i>"
    )
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_quiz_keyboard(word_id, options))


@router.callback_query(F.data == "mode_quiz")
@router.callback_query(F.data == "next_quiz")
async def cb_mode_quiz(call: CallbackQuery):
    await update_user_activity(call.from_user.id)
    await send_next_quiz(call)
    await call.answer()

@router.callback_query(F.data.startswith("answer_"))
async def cb_answer_quiz(call: CallbackQuery):
    parts = call.data.split("_")
    word_id = int(parts[1])
    opt_index = int(parts[2])
    user_id = call.from_user.id

    quiz_data = active_quizzes.get(f"{user_id}_{word_id}")

    if not quiz_data:
        # Если состояние сбросилось
        await call.answer("Загрузка следующего вопроса...")
        await send_next_quiz(call)
        return

    selected_option = quiz_data["options"][opt_index]
    correct_option = quiz_data["correct"]

    if selected_option == correct_option:
        await call.answer("👏 Правильно! Замечательная работа!", show_alert=True)
        await mark_word_as_learning(user_id, word_id)
    else:
        await call.answer(f"❌ Ошибка! Правильный перевод: {correct_option}", show_alert=True)
        await mark_word_as_learning(user_id, word_id)



    # Удаляем из кэша
    active_quizzes.pop(f"{user_id}_{word_id}", None)
    
    # Следующий вопрос
    await send_next_quiz(call)
