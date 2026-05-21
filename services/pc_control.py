import os
import subprocess
import psutil
import pyautogui
import ctypes
import math
import time
import shutil

GAME_MODE_KILL = [
    'chrome.exe', 'msedge.exe', 'browser.exe', 'spotify.exe', 
    'onedrive.exe', 'steamwebhelper.exe', 'epicgameslauncher.exe', 'discord.exe'
]

WHITE_LIST = [
    'explorer.exe', 'svchost.exe', 'taskmgr.exe', 'system', 'idle',
    'python.exe', 'telegram.exe', 'pyw.exe'
]

def get_game_mode_targets():
    """Возвращает список процессов, которые нужно закрыть."""
    targets = []
    for proc in psutil.process_iter(['name']):
        try:
            p_name = proc.info['name']
            if p_name and p_name.lower() in GAME_MODE_KILL and p_name.lower() not in WHITE_LIST:
                targets.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return targets

def get_trash_files():
    """Возвращает список всех мусорных файлов в Temp."""
    user_temp = os.environ.get('TEMP')
    system_temp = r"C:\Windows\Temp"
    
    targets = []
    for folder in [user_temp, system_temp]:
        if folder and os.path.exists(folder):
            for root, dirs, files in os.walk(folder):
                for file in files:
                    targets.append(os.path.join(root, file))
    return targets

def set_gamma(level_str: str):
    """Устанавливает программную гамму (Color Calibration)."""
    gamma_value = 1.0  # Default
    
    if level_str == "75":
        gamma_value = 1.5  # Увеличенная гамма (светлее)
    elif level_str == "100":
        gamma_value = 2.0  # Сильно увеличенная гамма (максимум)

    hdc = ctypes.windll.user32.GetDC(None)
    GammaArray = ((ctypes.c_ushort * 256) * 3)()
    
    for i in range(256):
        # Вычисление кривой гаммы
        val = int(math.pow(i / 255.0, 1.0 / gamma_value) * 65535)
        if val > 65535: val = 65535
        if val < 0: val = 0
        
        GammaArray[0][i] = val # Red
        GammaArray[1][i] = val # Green
        GammaArray[2][i] = val # Blue
        
    ctypes.windll.gdi32.SetDeviceGammaRamp(hdc, ctypes.byref(GammaArray))
    ctypes.windll.user32.ReleaseDC(None, hdc)

def is_explorer_running() -> bool:
    """Проверяет, запущен ли процесс проводника (explorer.exe)."""
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == 'explorer.exe':
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def toggle_explorer():
    """Убивает или запускает проводник Windows."""
    if is_explorer_running():
        os.system("taskkill /f /im explorer.exe")
    else:
        # Запускаем так, чтобы он работал корректно
        subprocess.Popen("explorer.exe")

def speak_text(text: str):
    """Озвучивает текст через встроенный синтезатор речи Windows (PowerShell)."""
    # Очищаем текст от кавычек, чтобы не сломать скрипт
    safe_text = text.replace('"', '').replace("'", "")
    
    script = f'Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.Speak("{safe_text}")'
    
    # Запуск в абсолютно скрытом режиме
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = 0 # Скрытое окно
    
    subprocess.Popen(["powershell", "-Command", script], startupinfo=startupinfo)

def get_performance_stats() -> str:
    """Возвращает статус системы."""
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    uptime = time.time() - psutil.boot_time()
    uptime_str = f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m"
    
    return f"⚡ **Статус системы:**\n\n" \
           f"🧠 CPU: {cpu}%\n" \
           f"💽 RAM: {ram.percent}% ({ram.used // (1024**3)}/{ram.total // (1024**3)} GB)\n" \
           f"⏱ Uptime: {uptime_str}"

def force_mem_clean():
    """Сброс кэшированной оперативной памяти (EmptyWorkingSet)."""
    psapi = ctypes.WinDLL('psapi', use_last_error=True)
    EmptyWorkingSet = psapi.EmptyWorkingSet
    EmptyWorkingSet.argtypes = [ctypes.c_void_p]
    
    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_SET_QUOTA = 0x0100
    
    cleaned_processes = 0
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            h_proc = ctypes.windll.kernel32.OpenProcess(
                PROCESS_QUERY_INFORMATION | PROCESS_SET_QUOTA, 
                False, 
                proc.info['pid']
            )
            if h_proc:
                if EmptyWorkingSet(h_proc):
                    cleaned_processes += 1
                ctypes.windll.kernel32.CloseHandle(h_proc)
        except Exception:
            continue
            
    return cleaned_processes

def clear_clipboard():
    """Очистка буфера обмена Windows."""
    try:
        ctypes.windll.user32.OpenClipboard(None)
        ctypes.windll.user32.EmptyClipboard()
        ctypes.windll.user32.CloseClipboard()
        return True
    except:
        return False

def clean_messengers_cache():
    """Очистка кэша Discord и Telegram (возвращает освобожденные МБ)."""
    appdata = os.getenv('APPDATA')
    localappdata = os.getenv('LOCALAPPDATA')
    deleted_bytes = 0
    
    paths_to_clean = []
    if appdata:
        paths_to_clean.append(os.path.join(appdata, 'discord', 'Cache'))
        paths_to_clean.append(os.path.join(appdata, 'discord', 'Code Cache'))
        paths_to_clean.append(os.path.join(appdata, 'Telegram Desktop', 'tdata', 'user_data', 'cache'))
        
    if localappdata:
        paths_to_clean.append(os.path.join(localappdata, 'FiveM', 'FiveM.app', 'cache'))
        paths_to_clean.append(os.path.join(localappdata, 'RAGEMP', 'client_resources'))
        
    for path in paths_to_clean:
        if os.path.exists(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(file_path)
                        os.remove(file_path)
                        deleted_bytes += size
                    except:
                        pass
                        
    return round(deleted_bytes / (1024**2), 2)

def get_all_processes():
    """Получает все процессы по потреблению оперативной памяти (свыше 10МБ)."""
    procs = []
    # Системные процессы, которые лучше скрыть, чтобы случайно не убить Windows
    ignore_list = ['system', 'idle', 'svchost.exe', 'explorer.exe', 'python.exe', 'pyw.exe', 'csrss.exe', 'smss.exe']
    
    for p in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            name = p.info['name']
            if not name or name.lower() in ignore_list:
                continue
                
            mem_mb = p.info['memory_info'].rss / (1024 * 1024)
            if mem_mb < 10:  # Игнорируем совсем мелкие процессы (меньше 10 МБ)
                continue
                
            procs.append({'pid': p.info['pid'], 'name': name, 'mem': mem_mb})
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
            
    # Сортируем по убыванию памяти
    return sorted(procs, key=lambda x: x['mem'], reverse=True)

def kill_process_by_pid(pid: int):
    """Убивает процесс по его ID."""
    try:
        p = psutil.Process(pid)
        name = p.name()
        p.terminate()
        return True, name
    except Exception:
        return False, ""

def take_screenshot() -> str:
    """Делает скриншот и возвращает путь к файлу."""
    path = "screenshot.png"
    pyautogui.screenshot(path)
    return path

def execute_system_command(command: str):
    """Выполняет системные команды."""
    
    # Специальная настройка для скрытого/фонового запуска в Windows
    # Флаг 7 = SW_SHOWMINNOACTIVE (Отображается свернутым, НЕ забирает фокус)
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = 7 

    if command == "sleep":
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    elif command == "shutdown":
        os.system("shutdown /s /t 0")
    elif command == "restart":
        os.system("shutdown /r /t 0")
    elif command == "taskmgr":
        subprocess.Popen("taskmgr", startupinfo=startupinfo)
    elif command == "steam":
        # Используем /MIN для фонового запуска
        subprocess.Popen("start /MIN steam://", shell=True, startupinfo=startupinfo)
    elif command == "discord":
        # Открытие Discord или Discord PTB в фоне
        appdata = os.getenv('LOCALAPPDATA')
        if appdata:
            ptb_path = os.path.join(appdata, "discordptb", "Update.exe")
            discord_path = os.path.join(appdata, "Discord", "Update.exe")
            
            if os.path.exists(ptb_path):
                # Добавляем флаг --start-minimized для Discord
                subprocess.Popen([ptb_path, "--processStart", "DiscordPTB.exe", "--start-minimized"], startupinfo=startupinfo)
            elif os.path.exists(discord_path):
                subprocess.Popen([discord_path, "--processStart", "Discord.exe", "--start-minimized"], startupinfo=startupinfo)
            else:
                 subprocess.Popen("start /MIN discord:", shell=True, startupinfo=startupinfo)
