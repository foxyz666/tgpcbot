from telegram import Update
from telegram.ext import ContextTypes
import asyncio
import os
import psutil
from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import restricted
from utils.keyboards import (get_gaming_menu, get_clean_menu, get_brightness_menu, 
                             get_system_menu, get_confirm_delete_menu, get_back_button, get_persistent_keyboard)
from services import pc_control
from utils.live import live_status_loop
from utils.i18n import set_lang, t

def draw_progress(percent: int) -> str:
    """Отрисовывает текстовый прогресс-бар."""
    length = 10
    filled = int(length * percent // 100)
    bar = '■' * filled + '□' * (length - filled)
    return f"[{bar}] {percent}%"

def generate_taskkiller_text(procs, page, per_page=8):
    """Генерирует текст с кликабельными моноширинными именами процессов."""
    total_pages = max(1, (len(procs) + per_page - 1) // per_page)
    start = page * per_page
    end = start + per_page
    page_procs = procs[start:end]
    
    text = t("top_procs").format(page + 1, total_pages)
    
    for p in page_procs:
        text += f"▪️ `{p['name']}` — {int(p['mem'])} MB\n"
        
    text += t("manual_kill")
    return text

async def process_trash_cleaning(query, context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    """Фоновая функция для очистки мусора с паузой на большие файлы."""
    targets = context.user_data.get('trash_targets', [])
    deleted_bytes = context.user_data.get('trash_deleted_bytes', 0)
    deleted_count = context.user_data.get('trash_deleted_count', 0)
    total_files = context.user_data.get('trash_total_files', len(targets))
    
    if total_files == 0:
        await query.edit_message_text("✨ Компьютер уже чист! Лишних файлов не найдено.", reply_markup=get_clean_menu())
        return

    # Защита от спама изменениями сообщений в Telegram
    last_percent_updated = -10
    
    while targets:
        file_path = targets.pop(0)
        
        try:
            if not os.path.exists(file_path):
                continue
                
            file_size = os.path.getsize(file_path)
            
            # Проверка на большой файл (> 150 MB)
            if file_size > 150 * 1024 * 1024:
                # Сохраняем прогресс перед паузой
                context.user_data['trash_targets'] = targets
                context.user_data['trash_deleted_bytes'] = deleted_bytes
                context.user_data['trash_deleted_count'] = deleted_count
                context.user_data['trash_current_big_file'] = file_path
                
                await query.edit_message_text(
                    f"⚠️ **Найден большой файл в Temp** ({round(file_size/(1024**2), 1)} MB).\n\n"
                    f"Путь: `{file_path}`\n\nУдалить его?", 
                    reply_markup=get_confirm_delete_menu(), 
                    parse_mode="Markdown"
                )
                return # Выходим из функции, ждем решения пользователя

            # Удаляем мелкий файл
            os.remove(file_path)
            deleted_bytes += file_size
            deleted_count += 1
            
        except Exception:
            pass # Файл занят или нет доступа
            
        # Обновление прогресс-бара (только каждые 20%, чтобы не словить FloodControl)
        processed = total_files - len(targets)
        percent = int(processed / total_files * 100)
        
        if percent - last_percent_updated >= 25 or not targets:
            last_percent_updated = percent
            try:
                await query.edit_message_text(
                    f"🧹 Идет очистка кэша и мусора...\n{draw_progress(percent)}"
                )
                await asyncio.sleep(0.5) # Пауза для Telegram API
            except:
                pass

    # Когда все файлы кончились
    mb_freed = round(deleted_bytes / (1024**2), 2)
    context.user_data.clear() # Очищаем кэш
    
    await query.edit_message_text(
        f"🧹 **Очистка завершена!**\n\n"
        f"🗑 Удалено файлов: {deleted_count}\n"
        f"💾 Освобождено места: {mb_freed} MB", 
        reply_markup=get_clean_menu(),
        parse_mode="Markdown"
    )

@restricted
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # --- ЯЗЫК (Language) ---
    if data.startswith("set_lang_"):
        lang_code = data.split("_")[2]
        set_lang(lang_code)
        # Отправляем новое сообщение, чтобы обновить нижнюю клавиатуру (persistent keyboard)
        await query.message.reply_text(t("lang_changed"), reply_markup=get_persistent_keyboard())
        await query.message.delete() # Удаляем старое меню выбора языка
        return

    # Отменяем Live Status при любом нажатии инлайн-кнопок
    if 'live_task' in context.user_data:
        context.user_data['live_task'].cancel()
        del context.user_data['live_task']
        
    if data == "menu_stop_live":
        await query.edit_message_text("✅ Мониторинг остановлен.", parse_mode="Markdown")
        return

    # --- НАВИГАЦИЯ ---
    if data == "menu_brightness":
        await query.edit_message_text(t("gamma"), reply_markup=get_brightness_menu(), parse_mode="Markdown")
    elif data == "menu_system":
        is_exp = pc_control.is_explorer_running()
        await query.edit_message_text(t("menu_sys"), reply_markup=get_system_menu(is_exp), parse_mode="Markdown")
    elif data == "menu_taskkiller":
        procs = pc_control.get_all_processes()
        from utils.keyboards import get_task_killer_menu
        text = generate_taskkiller_text(procs, 0)
        await query.edit_message_text(text, reply_markup=get_task_killer_menu(procs, 0), parse_mode="Markdown")

    # --- IN-BOT TASK KILLER (Paginație și Kill) ---
    elif data.startswith("taskpage_"):
        page = int(data.split("_")[1])
        procs = pc_control.get_all_processes()
        
        total_pages = max(1, (len(procs) + 8 - 1) // 8)
        if page >= total_pages: page = total_pages - 1
        if page < 0: page = 0
            
        from utils.keyboards import get_task_killer_menu
        text = generate_taskkiller_text(procs, page)
        await query.edit_message_text(text, reply_markup=get_task_killer_menu(procs, page), parse_mode="Markdown")

    elif data.startswith("killpid_"):
        parts = data.split("_")
        pid = int(parts[1])
        page = int(parts[2]) if len(parts) > 2 else 0
        
        success, name = pc_control.kill_process_by_pid(pid)
        
        # Обновляем список после убийства
        procs = pc_control.get_all_processes()
        from utils.keyboards import get_task_killer_menu
        
        msg = f"💀 Procesul `{name}` a fost ucis." if success else f"❌ Eroare la închiderea procesului."
        await query.answer(msg, show_alert=True) # Показываем всплывающее окно
        
        total_pages = max(1, (len(procs) + 8 - 1) // 8)
        if page >= total_pages: page = total_pages - 1
        
        text = generate_taskkiller_text(procs, page)
        await query.edit_message_text(text, reply_markup=get_task_killer_menu(procs, page), parse_mode="Markdown")

    # --- ИГРОВОЙ ЦЕНТР ---
    elif data == "opt_game":
        await query.edit_message_text("⏳ Подготовка игрового режима...")
        await asyncio.sleep(0.5)
        
        targets = pc_control.get_game_mode_targets()
        total_procs = len(targets)
        killed_count = 0
        ram_before = psutil.virtual_memory().available
        
        if total_procs == 0:
            await query.edit_message_text("🎮 **Игровой режим уже активен!** Лишних процессов нет.", reply_markup=get_gaming_menu(), parse_mode="Markdown")
            return
            
        # Убиваем процессы с отображением прогресса
        last_percent = 0
        for idx, proc in enumerate(targets):
            try:
                proc.terminate()
                killed_count += 1
            except:
                pass
                
            percent = int((idx + 1) / total_procs * 100)
            if percent - last_percent >= 25 or idx == total_procs - 1:
                last_percent = percent
                try:
                    await query.edit_message_text(f"🚀 Оптимизация процессов...\n{draw_progress(percent)}")
                    await asyncio.sleep(0.5)
                except:
                    pass
                    
        ram_after = psutil.virtual_memory().available
        freed_ram = max(0, round((ram_after - ram_before) / (1024**3), 2))
        
        await query.edit_message_text(
            f"🎮 **Игровой режим активирован!**\n\n"
            f"❌ Закрыто лишних процессов: {killed_count}\n"
            f"🧹 Освобождено RAM: {freed_ram} GB", 
            reply_markup=get_gaming_menu(), 
            parse_mode="Markdown"
        )
        # Автоматически сбрасываем кэш Working Set при игровом режиме
        pc_control.force_mem_clean()
        
    elif data == "opt_clean":
        await query.edit_message_text("🔍 Сканирование мусорных файлов...")
        await asyncio.sleep(0.5)
        
        targets = pc_control.get_trash_files()
        # Сохраняем в память сессии
        context.user_data['trash_targets'] = targets
        context.user_data['trash_deleted_bytes'] = 0
        context.user_data['trash_deleted_count'] = 0
        context.user_data['trash_total_files'] = len(targets)
        
        await process_trash_cleaning(query, context, query.message.chat_id)

    # --- DEEP CLEAN (Память и кэш) ---
    elif data.startswith("clean_"):
        if data == "clean_ram":
            cleaned = pc_control.force_mem_clean()
            await query.edit_message_text(
                f"🧠 **Память очищена!**\nСброшен кэш (Working Set) для {cleaned} процессов.", 
                reply_markup=get_clean_menu(), parse_mode="Markdown"
            )
        elif data == "clean_appcache":
            await query.edit_message_text("⏳ Идет удаление кэша Telegram, Discord и игр...")
            await asyncio.sleep(0.5)
            freed_mb = pc_control.clean_messengers_cache()
            await query.edit_message_text(
                f"💬 **Кэш очищен!**\nОсвобождено {freed_mb} MB места.", 
                reply_markup=get_clean_menu(), parse_mode="Markdown"
            )
        elif data == "clean_clip":
            success = pc_control.clear_clipboard()
            text = "📋 Буфер обмена **очищен**!" if success else "❌ Ошибка доступа к буферу обмена."
            await query.edit_message_text(text, reply_markup=get_clean_menu(), parse_mode="Markdown")

    # --- CONFIRM DELETE (Большие файлы) ---
    elif data.startswith("confirm_del_"):
        file_path = context.user_data.get('trash_current_big_file')
        if not file_path:
            await query.answer("Данные устарели", show_alert=True)
            return
            
        if data == "confirm_del_yes":
            try:
                file_size = os.path.getsize(file_path)
                os.remove(file_path)
                context.user_data['trash_deleted_bytes'] += file_size
                context.user_data['trash_deleted_count'] += 1
                await query.edit_message_text("✅ Файл удален. Продолжаю очистку...")
            except Exception:
                await query.edit_message_text("❌ Не удалось удалить файл (возможно занят). Продолжаю очистку...")
        else:
            await query.edit_message_text("⏭ Файл пропущен. Продолжаю очистку...")
            
        await asyncio.sleep(1)
        # Возобновляем очистку
        await process_trash_cleaning(query, context, query.message.chat_id)

    # --- GAMMA / BRIGHTNESS ---
    elif data.startswith("gamma_"):
        level = data.split("_")[1]
        pc_control.set_gamma(level)
        
        if level == "default":
            text = "💡 Гамма сброшена (По умолчанию)"
        else:
            text = f"💡 Гамма увеличена до {level}%"
            
        await query.edit_message_text(text, reply_markup=get_brightness_menu())

    # --- SYSTEM ---
    elif data.startswith("sys_"):
        cmd = data.split("_")[1]
        
        if cmd == "explorer":
            pc_control.toggle_explorer()
            await asyncio.sleep(0.5)  # Ждем полсекунды, чтобы Windows успела убить/запустить процесс
            is_exp = pc_control.is_explorer_running()
            await query.edit_message_reply_markup(reply_markup=get_system_menu(is_exp))
            
        elif cmd == "screenshot":
            await query.edit_message_text("📸 Делаю скриншот...", parse_mode="Markdown")
            path = pc_control.take_screenshot()
            with open(path, "rb") as photo:
                await context.bot.send_photo(chat_id=query.message.chat_id, photo=photo)
            os.remove(path)
            is_exp = pc_control.is_explorer_running()
            await query.message.reply_text("🖥 **Система:**", reply_markup=get_system_menu(is_exp), parse_mode="Markdown")
        elif cmd == "doupdate":
            from utils.updater import perform_update, restart_bot
            await query.edit_message_text("⏳ **Pasul 1/2:** Se descarcă actualizarea de pe GitHub...", parse_mode="Markdown")
            
            # Ne asigurăm că interfața Telegram a procesat mesajul de mai sus înainte de a bloca firul principal
            await asyncio.sleep(0.5)
            
            # Rulăm sincron. Va bloca botul 2-3 secunde, dar este cel mai sigur pe Windows.
            success, msg = perform_update()
            
            if success:
                await query.edit_message_text(f"✅ **Succes!**\n\n{msg}\n🔄 Botul se restartează acum...", parse_mode="Markdown")
                await asyncio.sleep(2)
                restart_bot()
            else:
                await query.edit_message_text(f"❌ **Eroare la actualizare:**\n`{msg}`", parse_mode="Markdown")
        elif cmd == "cancelupdate":
            await query.edit_message_text("❌ Update cancelled.", parse_mode="Markdown")
        else:
            actions = {
                "sleep": "Переход в спящий режим 💤",
                "restart": "Перезагрузка ПК 🔄",
                "shutdown": "Выключение ПК 🛑",
                "taskmgr": "Открыт Диспетчер задач 📊",
                "steam": "Запускаю Steam 🎮",
                "discord": "Запускаю Discord 💬"
            }
            pc_control.execute_system_command(cmd)
            is_exp = pc_control.is_explorer_running()
            await query.edit_message_text(actions[cmd], reply_markup=get_system_menu(is_exp))
