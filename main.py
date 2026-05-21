import logging
import threading
import asyncio
import os
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, Application

import config
from handlers.commands import start_command, update_command
from handlers.callbacks import button_handler
from handlers.messages import text_message_handler
from utils.keyboards import get_persistent_keyboard

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def create_image():
    # Создаем простую иконку (зеленый квадрат с белым кругом)
    image = Image.new('RGB', (64, 64), color=(40, 167, 69))
    dc = ImageDraw.Draw(image)
    dc.ellipse([16, 16, 48, 48], fill=(255, 255, 255))
    return image

async def post_init(application: Application):
    """Эта функция запускается один раз при старте бота."""
    try:
        await application.bot.send_message(
            chat_id=config.ALLOWED_USER_ID, 
            text="🚀 **Your PC is LIVE NOW!**\n\nКлавиатура снизу обновлена 👇", 
            reply_markup=get_persistent_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.error(f"Не удалось отправить сообщение о запуске: {e}")

def run_bot():
    # Создаем новый цикл событий для фонового потока
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    app = ApplicationBuilder().token(config.BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("update", update_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # Обработчик текстовых сообщений для озвучки и /kill команд
    # Убрали ~filters.COMMAND, чтобы бот мог ловить /kill в текстовом хендлере
    app.add_handler(MessageHandler(filters.TEXT, text_message_handler))
    
    print("✅ Бот успешно запущен в фоновом режиме!")
    app.run_polling()

def exit_action(icon, item):
    icon.stop()
    os._exit(0)  # Мгновенно завершаем работу всех процессов и бота

def main():
    if not config.BOT_TOKEN or config.BOT_TOKEN == "ТВОЙ_ТОКЕН_ЗДЕСЬ":
        print("ОШИБКА: Добавь BOT_TOKEN и свой ALLOWED_USER_ID в файл config.py")
        return

    # Запускаем самого Telegram бота в отдельном невидимом потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    # Запускаем иконку в системном трее в главном потоке (Windows требует этого)
    image = create_image()
    menu = (item('Выход (Закрыть бота)', exit_action),)
    icon = pystray.Icon("TelegramBot", image, "Telegram PC Bot", menu)
    
    icon.run()

if __name__ == '__main__':
    main()