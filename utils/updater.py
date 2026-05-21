import urllib.request
import json
import os
import sys
import zipfile
import io
import subprocess

# Версия вашего бота
CURRENT_VERSION = "1.0.4"

# ВАЖНО: Здесь нужно указать ваш репозиторий на GitHub (например "foxyz666/TelegramPCBot")
GITHUB_REPO = "foxyz666/tgpcbot" 

# Директория бота (чтобы избежать проблем, если бот запущен из другой папки)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL_FILE = os.path.join(BASE_DIR, "update_url.txt")

def check_for_updates():
    """Проверяет наличие новой версии (Release) на GitHub."""
    if not GITHUB_REPO:
        return False, None
        
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            latest_version = data.get("tag_name", "").replace("v", "")
            
            if latest_version and latest_version != CURRENT_VERSION:
                # Save download url for later
                with open(URL_FILE, "w") as f:
                    f.write(data["zipball_url"])
                return True, data
    except Exception as e:
        print(f"Eroare la verificarea update-ului: {e}")
    return False, None

def perform_update():
    """Скачивает ZIP с GitHub, распаковывает и заменяет старые файлы."""
    if not os.path.exists(URL_FILE):
        return False, "Update URL not found."
    
    with open(URL_FILE, "r") as f:
        download_url = f.read().strip()
        
    try:
        # 1. Download cu timeout
        req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            file_data = response.read()
            
        # 2. Extract
        with zipfile.ZipFile(io.BytesIO(file_data)) as archive:
            # Папка внутри архива GitHub (обычно user-repo-hash)
            root_folder = archive.namelist()[0]
            
            for item in archive.namelist():
                if item.endswith('/'): 
                    continue
                
                # ПРОПУСКАЕМ важные файлы, чтобы не удалить настройки пользователя!
                if "config.py" in item or "lang.txt" in item: 
                    continue
                
                source = archive.open(item)
                # Вычисляем правильный путь для распаковки относительно BASE_DIR
                relative_path = item.replace(root_folder, "")
                target_path = os.path.join(BASE_DIR, relative_path)
                
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                with open(target_path, "wb") as f:
                    f.write(source.read())
                    
        # Clean up the file
        if os.path.exists(URL_FILE):
            os.remove(URL_FILE)
            
        return True, "Update applied successfully!"
    except Exception as e:
        print(f"Update error: {e}")
        return False, str(e)

def restart_bot():
    """Перезагружает бота через системный скрипт VBS."""
    vbs_path = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\TelegramPCBot.vbs")
    
    if os.path.exists(vbs_path):
        os.startfile(vbs_path)
    else:
        # Если VBS нет, пробуем запустить стандартно
        subprocess.Popen(["pyw", "main.py"])
        
    os._exit(0) # Убиваем текущий процесс, чтобы новый занял его место