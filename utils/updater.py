import urllib.request
import json
import os
import sys
import zipfile
import io
import subprocess

# Версия вашего бота
CURRENT_VERSION = "1.0.0"

# ВАЖНО: Здесь нужно указать ваш репозиторий на GitHub (например "foxyz666/TelegramPCBot")
# Пока вы не загрузите код на GitHub, оставьте пустым ""
GITHUB_REPO = "foxyz666/tgpcbot" 

def check_for_updates():
    """Проверяет наличие новой версии (Release) на GitHub."""
    if not GITHUB_REPO:
        return False, None
        
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            latest_version = data.get("tag_name", "").replace("v", "")
            
            if latest_version and latest_version != CURRENT_VERSION:
                # Save download url for later
                with open("update_url.txt", "w") as f:
                    f.write(data["zipball_url"])
                return True, data
    except Exception as e:
        print(f"Eroare la verificarea update-ului: {e}")
    return False, None

def perform_update():
    """Скачивает ZIP с GitHub, распаковывает и заменяет старые файлы."""
    if not os.path.exists("update_url.txt"):
        return False, "Update URL not found."
    with open("update_url.txt", "r") as f:
        download_url = f.read().strip()
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            latest_version = data.get("tag_name", "").replace("v", "")
            
            if latest_version and latest_version != CURRENT_VERSION:
                download_url = data["zipball_url"]
                return {"version": latest_version, "url": download_url}
    except Exception as e:
        print(f"Eroare la verificarea update-ului: {e}")
    return None

def perform_update(download_url):
    """Скачивает ZIP с GitHub, распаковывает и заменяет старые файлы."""
    try:
        req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            with zipfile.ZipFile(io.BytesIO(response.read())) as archive:
                # Папка внутри архива GitHub (обычно user-repo-hash)
                root_folder = archive.namelist()[0]
                
                for item in archive.namelist():
                    if item.endswith('/'): 
                        continue
                    
                    # ПРОПУСКАЕМ важные файлы, чтобы не удалить настройки пользователя!
                    if "config.py" in item or "lang.txt" in item: 
                        continue
                    
                    source = archive.open(item)
                    # Вычисляем правильный путь для распаковки
                    relative_path = item.replace(root_folder, "")
                    target_path = os.path.join(os.getcwd(), relative_path)
                    
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with open(target_path, "wb") as f:
                        f.write(source.read())
        
        # Clean up the file
        if os.path.exists("update_url.txt"):
            os.remove("update_url.txt")
            
        return True, "Update applied successfully. Please restart the bot to apply changes."
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