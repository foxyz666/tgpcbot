from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from utils.i18n import t

def get_persistent_keyboard():
    keyboard = [
        [KeyboardButton(t("system")), KeyboardButton(t("gaming"))],
        [KeyboardButton(t("clean_pc")), KeyboardButton(t("status"))],
        [KeyboardButton(t("lang"))]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)

def get_gaming_menu():
    keyboard = [
        [InlineKeyboardButton(t("game_mode"), callback_data="opt_game")],
        [InlineKeyboardButton(t("gamma"), callback_data="menu_brightness")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_clean_menu():
    keyboard = [
        [InlineKeyboardButton(t("trash"), callback_data="opt_clean")],
        [InlineKeyboardButton(t("ram"), callback_data="clean_ram")],
        [InlineKeyboardButton(t("appcache"), callback_data="clean_appcache")],
        [InlineKeyboardButton(t("clip"), callback_data="clean_clip")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_lang_menu():
    keyboard = [
        [InlineKeyboardButton("🇷🇴 Română", callback_data="set_lang_ro")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang_ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_confirm_delete_menu():
    keyboard = [
        [InlineKeyboardButton(t("yes_delete"), callback_data="confirm_del_yes"),
         InlineKeyboardButton(t("no_keep"), callback_data="confirm_del_no")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_brightness_menu():
    keyboard = [
        [InlineKeyboardButton("Reset (Default)", callback_data="gamma_default")],
        [InlineKeyboardButton("Gamma 75%", callback_data="gamma_75"),
         InlineKeyboardButton("Gamma 100%", callback_data="gamma_100")],
        [InlineKeyboardButton(t("back"), callback_data="menu_gaming")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_system_menu(explorer_running=True):
    exp_text = f"✅ {t('explorer')}: ON" if explorer_running else f"❌ {t('explorer')}: OFF"
    
    keyboard = [
        [InlineKeyboardButton(t("in_bot_taskmgr"), callback_data="menu_taskkiller")],
        [InlineKeyboardButton(t("screenshot"), callback_data="sys_screenshot")],
        [InlineKeyboardButton(exp_text, callback_data="sys_explorer")],
        [InlineKeyboardButton(t("sleep"), callback_data="sys_sleep"),
         InlineKeyboardButton(t("restart"), callback_data="sys_restart"),
         InlineKeyboardButton(t("shutdown"), callback_data="sys_shutdown")],
        [InlineKeyboardButton("🎮 Steam", callback_data="sys_steam"),
         InlineKeyboardButton("💬 Discord", callback_data="sys_discord")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_task_killer_menu(procs, page=0, per_page=8):
    keyboard = []
    total_pages = max(1, (len(procs) + per_page - 1) // per_page)
    
    start = page * per_page
    end = start + per_page
    page_procs = procs[start:end]
    
    # Adaugam fiecare proces ca un buton
    for p in page_procs:
        btn_text = f"💀 {p['name']} ({int(p['mem'])} MB)"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"killpid_{p['pid']}_{page}")])
        
    # Butoane de navigare (pagini)
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"taskpage_{page-1}"))
        
    nav_row.append(InlineKeyboardButton(f"🔄 {page+1}/{total_pages}", callback_data=f"taskpage_{page}"))
    
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"taskpage_{page+1}"))
        
    keyboard.append(nav_row)
    keyboard.append([InlineKeyboardButton(t("back"), callback_data="menu_system")])
    return InlineKeyboardMarkup(keyboard)

def get_update_menu():
    keyboard = [
        [InlineKeyboardButton("✅ Да, обновить / Da, actualizați", callback_data="sys_doupdate")],
        [InlineKeyboardButton("❌ Нет / Nu acum", callback_data="sys_cancelupdate")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_button():
    # Эта кнопка отменяет Live Status при выходе
    keyboard = [[InlineKeyboardButton(t("stop_live"), callback_data="menu_stop_live")]]
    return InlineKeyboardMarkup(keyboard)
