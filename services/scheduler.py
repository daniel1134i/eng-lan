from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from datetime import datetime
from database.models import get_users_for_reminder_hour, get_quiz_question, get_user_stats
from keyboards.inline import get_quiz_keyboard
from handlers.quiz import active_quizzes

async def send_hourly_reminders(bot: Bot):
    current_hour = datetime.utcnow().hour
    user_ids = await get_users_for_reminder_hour(current_hour)
    
    if not user_ids:
        return

    for uid in user_ids:
        try:
            word, options = await get_quiz_question(uid)
            stats = await get_user_stats(uid)
            if word and options:
                word_id = word['word_id']
                active_quizzes[f"{uid}_{word_id}"] = {
                    "correct": word['translation'],
                    "options": options
                }
                learned = stats['learned_words']
                total = stats['total_words']
                pct = (learned / total * 100) if total > 0 else 0

                text = (
                    f"⚡ <b>Ежедневный Экспресс-Тест!</b> 📊 <code>{learned}/{total} ({pct:.1f}%)</code>\n\n"
                    f"Как переводится слово: <b>{word['english_word'].capitalize()}</b>?\n"
                    f"<i>Ответь за 3 секунды прямо в уведомлении! 👇</i>"
                )
                await bot.send_message(uid, text, parse_mode="HTML", reply_markup=get_quiz_keyboard(word_id, options))
        except Exception:
            pass

def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="UTC")
    # Проверка каждый час в начале часа (:00)
    scheduler.add_job(send_hourly_reminders, trigger="cron", minute=0, args=[bot])
    return scheduler


