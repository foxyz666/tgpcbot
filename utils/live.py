import asyncio
from telegram.ext import ContextTypes
from services import pc_control
from utils.keyboards import get_back_button

async def live_status_loop(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int):
    """Асинхронный цикл для постоянного обновления сообщения со статусом ПК."""
    try:
        # Будет обновляться 60 раз с задержкой 3 секунды (хватит на 3 минуты живого мониторинга)
        # Это сделано для того, чтобы Telegram не заблокировал бота за слишком частые запросы
        for _ in range(60):
            await asyncio.sleep(3)
            stats = pc_control.get_performance_stats() + "\n\n🔴 *Live Monitor (Обновляется автоматически...)*"
            try:
                await context.bot.edit_message_text(
                    stats,
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=get_back_button(),
                    parse_mode="Markdown"
                )
            except Exception as e:
                # Если сообщение не изменилось (например, CPU тот же), Telegram выдаст ошибку, мы ее игнорируем
                if "Message is not modified" in str(e):
                    continue
                # Если пользователь удалил сообщение или нажал другую кнопку, выходим из цикла
                break 
    except asyncio.CancelledError:
        pass # Задача была отменена вручную (пользователь вышел из меню)