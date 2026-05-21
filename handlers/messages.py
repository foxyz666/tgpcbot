import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import restricted
from services import pc_control
from utils.keyboards import get_system_menu, get_gaming_menu, get_clean_menu, get_lang_menu, get_back_button
from utils.i18n import t, get_all_translations
from utils.live import live_status_loop

@restricted
async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        return
        
    # Отменяем предыдущее фоновое обновление (если оно работало)
    if 'live_task' in context.user_data:
        context.user_data['live_task'].cancel()
        del context.user_data['live_task']
        
    # Обработка новой мультиязычной клавиатуры
    if text in get_all_translations("system"):
        is_exp = pc_control.is_explorer_running()
        await update.message.reply_text(t("menu_sys"), reply_markup=get_system_menu(is_exp), parse_mode="Markdown")
        return
    elif text in get_all_translations("gaming"):
        await update.message.reply_text(t("menu_game"), reply_markup=get_gaming_menu(), parse_mode="Markdown")
        return
    elif text in get_all_translations("clean_pc"):
        await update.message.reply_text(t("menu_clean"), reply_markup=get_clean_menu(), parse_mode="Markdown")
        return
    elif text in get_all_translations("lang"):
        await update.message.reply_text(t("menu_lang"), reply_markup=get_lang_menu(), parse_mode="Markdown")
        return
    elif text in get_all_translations("status"):
        stats = pc_control.get_performance_stats() + "\n\n🔴 *Live Monitor*"
        msg = await update.message.reply_text(stats, reply_markup=get_back_button(), parse_mode="Markdown")
        
        task = asyncio.create_task(live_status_loop(context, update.message.chat_id, msg.message_id))
        context.user_data['live_task'] = task
        return

    # --- КОМАНДЫ ЧЕРЕЗ ТЕКСТ ---
    if text.startswith("/kill "):
        process_name = text.split(" ", 1)[1]
        import os
        # Команда taskkill для Windows. Убьет процесс даже если он "Not Responding"
        result = os.system(f"taskkill /f /im {process_name} /t")
        
        if result == 0:
            await update.message.reply_text(f"💀 Procesul `{process_name}` a fost ucis cu succes (Forced Kill).", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"❌ Eroare: Procesul `{process_name}` nu a fost găsit sau nu ai permisiuni suficiente.", parse_mode="Markdown")
        return
        
    if text.startswith("/start"):
        return # Игнорируем, так как для start есть свой handler

    # Если это обычный текст - передаем в функцию озвучки
    pc_control.speak_text(text)
    await update.message.reply_text(f"🗣 Озвучено: {text}")