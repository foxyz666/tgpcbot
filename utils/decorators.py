from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
import config

def restricted(func):
    """Декоратор для ограничения доступа только для владельца."""
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id != config.ALLOWED_USER_ID:
            print(f"Попытка доступа от неавторизованного ID: {user_id}")
            return
        return await func(update, context, *args, **kwargs)
    return wrapped
