import os

# Salvăm limba direct în folderul botului (cale absolută)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANG_FILE = os.path.join(BASE_DIR, "lang.txt")

def get_lang():
    if os.path.exists(LANG_FILE):
        with open(LANG_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return "ro" # Setăm Româna ca limbă implicită (default)

def set_lang(lang):
    with open(LANG_FILE, "w", encoding="utf-8") as f:
        f.write(lang)

T = {
    "ru": {
        "system": "🖥 Система",
        "gaming": "🎮 Игровой центр",
        "clean_pc": "🧹 Очистка ПК",
        "status": "⚡ Статус",
        "lang": "🌐 Язык",
        "game_mode": "🎮 Запустить Игровой режим",
        "gamma": "💡 Настройка Гаммы (Gamma)",
        "trash": "🗑 Очистка мусора (Temp)",
        "ram": "🧠 Сброс кэша RAM",
        "appcache": "💬 Кэш мессенджеров (Discord/TG)",
        "clip": "📋 Очистить буфер обмена",
        "back": "⬅ Назад",
        "stop_live": "❌ Остановить монитор",
        "screenshot": "📸 Скриншот",
        "explorer": "Проводник",
        "sleep": "🔌 Спящий режим",
        "restart": "🔄 Перезагрузка",
        "shutdown": "🛑 Выключение",
        "taskmgr": "📊 Диспетчер задач",
        "in_bot_taskmgr": "🔫 Диспетчер задач",
        "top_procs": "📊 **Топ процессов по RAM - Страница {}/{}**\n\nНажмите на кнопку, чтобы убить процесс, или кликните на название ниже, чтобы скопировать его:\n",
        "manual_kill": "\n\n💡 *Отправьте* `/kill <имя_процесса>` *для ручного закрытия.*",
        "refresh": "🔄 Обновить",
        "menu_main": "🖥 **Главное меню:**",
        "menu_sys": "🖥 **Системные настройки:**",
        "menu_game": "🎮 **Игровой центр:**",
        "menu_clean": "🧹 **Глубокая очистка ПК:**",
        "menu_lang": "🌐 **Выберите язык / Choose Language / Alegeți limba:**",
        "lang_changed": "✅ Язык изменен на Русский!",
        "yes_delete": "✅ Да, удалить",
        "no_keep": "❌ Нет, оставить"
    },
    "ro": {
        "system": "🖥 Sistem",
        "gaming": "🎮 Centru de Jocuri",
        "clean_pc": "🧹 Curățare PC",
        "status": "⚡ Stare (Status)",
        "lang": "🌐 Limbă",
        "game_mode": "🎮 Pornește Modul de Joc",
        "gamma": "💡 Setări Gamă (Gamma)",
        "trash": "🗑 Curățare Fișiere (Temp)",
        "ram": "🧠 Resetare Cache RAM",
        "appcache": "💬 Cache Mesagerii (Discord/TG)",
        "clip": "📋 Golește Clipboard-ul",
        "back": "⬅ Înapoi",
        "stop_live": "❌ Oprire monitor",
        "screenshot": "📸 Captură de ecran",
        "explorer": "Explorer",
        "sleep": "🔌 Mod Sleep",
        "restart": "🔄 Restart",
        "shutdown": "🛑 Închide PC",
        "taskmgr": "📊 Task Manager",
        "in_bot_taskmgr": "🔫 Task Killer",
        "top_procs": "📊 **Top procese (RAM) - Pagina {}/{}**\n\nApasă butonul pentru a-l închide sau dă click pe nume pentru a-l copia:\n",
        "manual_kill": "\n\n💡 *Trimite* `/kill <nume_proces>` *pentru a-l opri manual.*",
        "refresh": "🔄 Reîmprospătare",
        "menu_main": "🖥 **Meniul principal:**",
        "menu_sys": "🖥 **Setări de sistem:**",
        "menu_game": "🎮 **Centrul de jocuri:**",
        "menu_clean": "🧹 **Curățare profundă a PC-ului:**",
        "menu_lang": "🌐 **Alegeți limba / Choose Language:**",
        "lang_changed": "✅ Limba a fost schimbată în Română!",
        "yes_delete": "✅ Da, șterge",
        "no_keep": "❌ Nu, păstrează"
    },
    "en": {
        "system": "🖥 System",
        "gaming": "🎮 Gaming Center",
        "clean_pc": "🧹 Deep Clean",
        "status": "⚡ Status",
        "lang": "🌐 Language",
        "game_mode": "🎮 Start Gaming Mode",
        "gamma": "💡 Gamma Settings",
        "trash": "🗑 Clean Trash (Temp)",
        "ram": "🧠 Reset RAM Cache",
        "appcache": "💬 Messengers Cache",
        "clip": "📋 Clear Clipboard",
        "back": "⬅ Back",
        "stop_live": "❌ Stop Monitor",
        "screenshot": "📸 Screenshot",
        "explorer": "Explorer",
        "sleep": "🔌 Sleep",
        "restart": "🔄 Restart",
        "shutdown": "🛑 Shutdown",
        "taskmgr": "📊 Task Manager",
        "in_bot_taskmgr": "🔫 Task Killer",
        "top_procs": "📊 **Top processes (RAM) - Page {}/{}**\n\nClick a button to kill it or click the name below to copy:\n",
        "manual_kill": "\n\n💡 *Send* `/kill <process_name>` *to kill manually.*",
        "refresh": "🔄 Refresh",
        "menu_main": "🖥 **Main Menu:**",
        "menu_sys": "🖥 **System Settings:**",
        "menu_game": "🎮 **Gaming Center:**",
        "menu_clean": "🧹 **Deep PC Clean:**",
        "menu_lang": "🌐 **Choose Language:**",
        "lang_changed": "✅ Language changed to English!",
        "yes_delete": "✅ Yes, delete",
        "no_keep": "❌ No, keep it"
    }
}

def t(key):
    lang = get_lang()
    return T.get(lang, T["ro"]).get(key, key) # Default fallback la Română

def get_all_translations(key):
    return [T["ru"][key], T["ro"][key], T["en"][key]]
