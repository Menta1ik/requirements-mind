#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import subprocess
import platform

# Определение цветов терминала
C_CYAN = "\033[96m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_RED = "\033[91m"
C_BOLD = "\033[1m"
C_RESET = "\033[0m"

def print_color(text, color_code):
    """Печатает текст с подсветкой, если терминал поддерживает цвета."""
    # Проверяем, поддерживает ли терминал цвета
    if sys.stdout.isatty():
        print(f"{color_code}{text}{C_RESET}")
    else:
        print(text)

def print_panel(text, title="", color_code=C_GREEN):
    """Отрисовывает красивую терминальную панель (рамку) вокруг текста."""
    lines = text.split("\n")
    max_len = max(len(l) for l in lines)
    if title:
        max_len = max(max_len, len(title) + 4)
    
    border_top = f"┏━ {title} " + "━" * (max_len - len(title) - 4) + "┓"
    if not title:
        border_top = "┏" + "━" * (max_len + 2) + "┓"
        
    print_color(border_top, color_code)
    for line in lines:
        padding = " " * (max_len - len(line))
        if sys.stdout.isatty():
            print(f"{color_code}┃{C_RESET} {line}{padding} {color_code}┃{C_RESET}")
        else:
            print(f"| {line}{padding} |")
            
    border_bottom = "┗" + "━" * (max_len + 2) + "┛"
    print_color(border_bottom, color_code)

def draw_banner():
    """Рисует приветственный баннер."""
    banner = fr"""
{C_CYAN}  ____                                                              _         __  __ _           _ 
 |  _ \ ___  __ _ _   _ _ _ __ ___ _ __ ___   ___  _ __  _ __  ___  | \/ | ___|  \/  (_)_ __   __| |
 | |_) / _ \/ _` | | | | | '__/ _ \ '_ ` _ \ / _ \| '_ \| '_ \/ __| | |\/| / _ \ |\/| | | '_ \ / _` |
 |  _ <  __/ (_| | |_| | | | |  __/ | | | | |  __/| | | | | | \__ \ | |  |  __/ |  | | | | | | (_| |
 |_| \_\___|\__, |\__,_|_|_|  \___|_| |_| |_|\___||_| |_|_| |_|___/ |_|  |_|\___|_|  |_|_|_| |_|\__,_|
            |___/                                                                                    {C_RESET}
    """
    print(banner)
    print_panel(
        "Добро пожаловать в Requirements Mind!\n"
        "Интерактивный установщик локального рабочего окружения.\n\n"
        "Этот скрипт подготовит Python-зависимости, свяжет ИИ-навыки с вашей IDE,\n"
        "настроит базу знаний Obsidian Vault и Google NotebookLM.",
        title=" Requirements Mind v2.0 Setup ",
        color_code=C_CYAN
    )

def detect_and_bootstrap():
    """Фаза 0: Проверяет наличие файлов ядра в текущей папке. Если их нет, скачивает дистрибутив с GitHub."""
    required_files = ["cli.py", "requirements.txt"]
    required_folders = ["skills", "kb"]
    
    is_installed = all(os.path.exists(f) for f in required_files) and \
                   all(os.path.exists(d) and os.path.isdir(d) for d in required_folders)
                   
    if is_installed:
        return
        
    print_color("\n⚠️  Внимание: В текущей папке не обнаружены файлы ядра Requirements Mind.", C_YELLOW)
    print_color("🚀 Запущена процедура глобальной bootstrap-установки с нуля!", C_CYAN)
    
    ans = input("Хотите скачать и развернуть дистрибутив в текущую папку? [Y/n]: ").strip().lower()
    if ans not in ('', 'y', 'yes'):
        print_color("❌ Установка отменена пользователем.", C_RED)
        sys.exit(0)
        
    url = "https://github.com/Menta1ik/requirements-mind/archive/refs/heads/main.zip"
    print(f"  • Скачивание дистрибутива из {url} ... ", end="", flush=True)
    
    import urllib.request
    import zipfile
    import tempfile
    
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            zip_data = response.read()
        print_color("OK", C_GREEN)
    except Exception as e:
        print_color("ОШИБКА", C_RED)
        print(f"Не удалось скачать дистрибутив: {e}")
        sys.exit(1)
        
    print("  • Распаковка файлов дистрибутива ... ", end="", flush=True)
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, "dist.zip")
            with open(zip_path, "wb") as f:
                f.write(zip_data)
                
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)
                
            extracted_items = os.listdir(temp_dir)
            dist_folder_name = None
            for item in extracted_items:
                if item.startswith("requirements-mind") and os.path.isdir(os.path.join(temp_dir, item)):
                    dist_folder_name = item
                    break
                    
            if not dist_folder_name:
                raise Exception("Не удалось найти корневую папку дистрибутива в архиве.")
                
            dist_folder_path = os.path.join(temp_dir, dist_folder_name)
            
            # Копируем всё содержимое в текущую папку
            for root, dirs, files in os.walk(dist_folder_path):
                rel_path = os.path.relpath(root, dist_folder_path)
                target_root = os.getcwd() if rel_path == "." else os.path.join(os.getcwd(), rel_path)
                
                if rel_path != ".":
                    os.makedirs(target_root, exist_ok=True)
                    
                for file in files:
                    if rel_path == "." and file == "install.py":
                        continue
                    src_file = os.path.join(root, file)
                    dest_file = os.path.join(target_root, file)
                    shutil.copy2(src_file, dest_file)
                    
        print_color("OK", C_GREEN)
        print_panel(
            "Все файлы ядра Requirements Mind успешно загружены!\n"
            "Переходим к интерактивной настройке окружения.",
            title=" Загрузка завершена ",
            color_code=C_GREEN
        )
    except Exception as e:
        print_color("ОШИБКА", C_RED)
        print(f"Не удалось распаковать дистрибутив: {e}")
        sys.exit(1)

def check_environment():
    """Шаг 1: Проверка базового окружения."""
    print_color("\n🔍 Шаг 1: Проверка базового системного окружения...", C_BOLD)
    
    # 1. Проверка версии Python
    py_version = sys.version_info
    print(f"  • Версия Python: {py_version.major}.{py_version.minor}.{py_version.micro} ... ", end="")
    if py_version.major < 3 or (py_version.major == 3 and py_version.minor < 10):
        print_color("НЕПОДДЕРЖИВАЕМАЯ", C_RED)
        print_panel(
            "Ошибка: Requirements Mind требует версию Python 3.10 или выше.\n"
            "Пожалуйста, обновите Python и запустите установщик снова.",
            title=" Ошибка Python ",
            color_code=C_RED
        )
        sys.exit(1)
    else:
        print_color("OK", C_GREEN)
        
    # 2. Проверка Git
    print("  • Проверка Git ... ", end="")
    git_path = shutil.which("git")
    if not git_path:
        print_color("НЕ НАЙДЕН", C_RED)
        print_panel(
            "Предупреждение: Git не обнаружен в вашей системе.\n"
            "Requirements Mind использует Git для совместной работы нескольких аналитиков\n"
            "и версионирования требований.\n\n"
            "Рекомендуем установить Git: https://git-scm.com/",
            title=" Предупреждение о Git ",
            color_code=C_YELLOW
        )
    else:
        try:
            res = subprocess.run(["git", "--version"], capture_output=True, text=True)
            print_color(f"OK ({res.stdout.strip()})", C_GREEN)
        except Exception:
            print_color("OK", C_GREEN)

def setup_virtualenv():
    """Шаг 2: Создание виртуального окружения и установка зависимостей."""
    print_color("\n📦 Шаг 2: Настройка виртуального окружения и зависимостей...", C_BOLD)
    
    # 1. Проверяем наличие uv
    uv_path = shutil.which("uv")
    use_uv = False
    
    if uv_path:
        print_color("  • Обнаружен uv! Установка будет выполнена в 10 раз быстрее.", C_GREEN)
        use_uv = True
    else:
        ans = input(f"  • [Опционально] Хотите установить 'uv' для сверхбыстрого запуска зависимостей? [y/N]: ").strip().lower()
        if ans in ('y', 'yes'):
            print("  • Попытка установки uv...")
            try:
                # Пытаемся установить uv глобально через pip
                subprocess.run([sys.executable, "-m", "pip", "install", "uv"], check=True)
                uv_path = shutil.which("uv")
                if uv_path:
                    print_color("  • 'uv' успешно установлен!", C_GREEN)
                    use_uv = True
            except Exception:
                print_color("  • Не удалось установить uv. Будет использован стандартный pip.", C_YELLOW)
                
    # 2. Создаем виртуальное окружение
    venv_dir = ".venv"
    if not os.path.exists(venv_dir):
        print(f"  • Создание виртуального окружения в папке '{venv_dir}' ... ", end="")
        try:
            if use_uv:
                subprocess.run(["uv", "venv", venv_dir], check=True, capture_output=True)
            else:
                subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
            print_color("OK", C_GREEN)
        except Exception as e:
            print_color("ОШИБКА", C_RED)
            print(f"Не удалось создать venv: {e}")
            sys.exit(1)
    else:
        print_color(f"  • Виртуальное окружение '{venv_dir}' уже существует. Пропускаем создание.", C_CYAN)

    # 3. Опеределяем пути к исполняемым файлам venv
    if platform.system() == "Windows":
        pip_path = os.path.join(venv_dir, "Scripts", "pip")
        python_path = os.path.join(venv_dir, "Scripts", "python")
    else:
        pip_path = os.path.join(venv_dir, "bin", "pip")
        python_path = os.path.join(venv_dir, "bin", "python")

    # 4. Установка зависимостей
    print("  • Установка необходимых библиотек (Rich, Pydantic, Playwright)... ")
    try:
        if use_uv:
            subprocess.run(["uv", "pip", "install", "-r", "requirements.txt"], check=True)
        else:
            subprocess.run([pip_path, "install", "-U", "pip"], check=True, capture_output=True)
            subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        print_color("  • Все зависимости успешно установлены!", C_GREEN)
    except Exception as e:
        print_color(f"  • Ошибка при установке зависимостей: {e}", C_RED)
        sys.exit(1)

    return python_path

def setup_ide_integration(python_path):
    """Шаг 3: Настройка ИИ-навыков в IDE."""
    print_color("\n💻 Шаг 3: Интеграция ИИ-ассистентов IDE...", C_BOLD)
    print(
        "Requirements Mind версии 2.0 использует IDE-Native ИИ-ассистентов.\n"
        "Мы свяжем наши ИИ-навыки (skills) со служебными папками ваших сред разработки.\n"
    )
    
    print("Выберите ваш ИИ-ассистент:")
    print("  [1] Cursor / VS Code + Copilot  (рекомендуется)")
    print("  [2] Claude Code")
    print("  [3] Google Antigravity")
    print("  [4] OpenAI Codex CLI")
    print("  [5] Все вышеперечисленные")
    print("  [6] Пропустить этот шаг")
    
    choice = input(f"\nВведите номер выбора [1-6, по умолчанию 1]: ").strip()
    if not choice:
        choice = "1"
        
    if choice == "6":
        # Подсказка с правильным именем Python для текущей ОС
        py_hint = "python" if platform.system() == "Windows" else "python3"
        print_color(f"  • Шаг пропущен. Вы можете связать их позже вручную: `{py_hint} cli.py setup-ide`.", C_YELLOW)
        return
        
    print("  • Привязка навыков в IDE...")
    try:
        # Вызываем встроенный обработчик в cli.py через python из venv
        subprocess.run([python_path, "cli.py", "setup-ide"], check=True)
    except Exception as e:
        print_color(f"  • Ошибка при настройке IDE: {e}", C_RED)

def setup_obsidian_integration(python_path):
    """Шаг 4: Настройка Obsidian."""
    print_color("\n📓 Шаг 4: Настройка визуализации в Obsidian...", C_BOLD)
    ans = input("Хотите настроить Obsidian Vault для интерактивного графа требований? [Y/n]: ").strip().lower()
    if ans in ('', 'y', 'yes'):
        vault_dir = "vault"
        os.makedirs(vault_dir, exist_ok=True)
        print_color(f"  • Локальный каталог '{vault_dir}/' подготовлен.", C_GREEN)
        print("  • Синхронизация файлов с Obsidian...")
        try:
            subprocess.run([python_path, "cli.py", "sync-vault"], check=True)
            print_color("  • Успешно синхронизировано!", C_GREEN)
        except Exception as e:
            print_color(f"  • Не удалось выполнить синхронизацию: {e}", C_RED)
        return True
    else:
        print_color("  • Шаг пропущен.", C_YELLOW)
        return False

def setup_notebooklm_integration():
    """Шаг 5: Настройка Google NotebookLM."""
    print_color("\n📤 Шаг 5: Настройка Google NotebookLM...", C_BOLD)
    ans = input("Хотите инициализировать папку экспорта для Google NotebookLM? [Y/n]: ").strip().lower()
    if ans in ('', 'y', 'yes'):
        os.makedirs("notebooklm", exist_ok=True)
        print_color("  • Локальный каталог 'notebooklm/' успешно создан.", C_GREEN)
        return True
    else:
        print_color("  • Шаг пропущен.", C_YELLOW)
        return False

def setup_demo_project(python_path, notebooklm_enabled):
    """Шаг 6: Инициализация демонстрационного проекта."""
    print_color("\n🚀 Шаг 6: Создание демонстрационного проекта...", C_BOLD)
    ans = input("Хотите развернуть готовый демо-проект для быстрого ознакомления? [Y/n]: ").strip().lower()
    if ans in ('', 'y', 'yes'):
        project_name = "demo-project"
        print(f"  • Инициализация проекта '{project_name}' ... ", end="")
        try:
            subprocess.run([python_path, "cli.py", "init", "--project", project_name], check=True, capture_output=True)
            subprocess.run([python_path, "cli.py", "onboard", "--project", project_name], check=True, capture_output=True)
            print_color("OK", C_GREEN)
        except Exception as e:
            print_color("ОШИБКА", C_RED)
            print(f"Не удалось инициализировать демо-проект: {e}")
            return
            
        # Записываем демонстрационные сырые требования
        input_req_file = f"projects/{project_name}/input/requirements.md"
        demo_requirements = """# Демонстрационные требования: Сервис доставки еды "БыстроБайт"

## 1. Описание концепции
Мы хотим запустить мобильное приложение и веб-сайт для ультрабыстрой доставки готовой еды из наших dark-kitchens.
Время доставки не должно превышать 20 минут с момента заказа.

## 2. Основной функционал (MVP)
* Авторизация пользователя по номеру телефона и одноразовому СМС-коду.
* Интерактивная карта для выбора адреса доставки (с проверкой зоны покрытия доставки).
* Каталог меню с возможностью добавления блюд в корзину и учета аллергенов.
* Оплата банковской картой или через СБП.
* Отслеживание курьера на карте в реальном времени.

## 3. Нефункциональные требования
* Приложение должно работать даже при слабом 3G интернете.
* Высокая отказоустойчивость в пиковые часы (с 12:00 до 14:00 и с 19:00 до 21:00).
"""
        try:
            with open(input_req_file, "w", encoding="utf-8") as f:
                f.write(demo_requirements)
            print_color(f"  • Демонстрационные требования записаны в {input_req_file}", C_GREEN)
        except Exception as e:
            print(f"  • Не удалось записать демо-требования: {e}")
            
        # Если NotebookLM включен, сразу генерируем демо-экспорт
        if notebooklm_enabled:
            print("  • Автоматическая генерация демо-экспорта для Google NotebookLM...")
            try:
                subprocess.run([python_path, "cli.py", "export-notebooklm", "--project", project_name], check=True, capture_output=True)
                print_color(f"  • Готовый файл экспорта создан по пути: notebooklm/{project_name}.json", C_GREEN)
            except Exception as e:
                print(f"  • Ошибка генерации демо-экспорта для NotebookLM: {e}")
        return True
    else:
        print_color("  • Шаг пропущен.", C_YELLOW)
        return False

def show_welcome_tour(obsidian_enabled, notebooklm_enabled):
    """Выводит шпаргалку и поздравление."""
    welcome_text = (
        "Поздравляем! Requirements Mind полностью установлен и настроен!\n\n"
        f"{C_BOLD}БЫСТРЫЙ СТАРТ ДЛЯ АНАЛИТИКА:{C_RESET}\n"
        "• Для демонстрационного проекта (demo-project):\n"
        "  1. Откройте чат ИИ-ассистента в вашей IDE и запустите Intake:\n"
        f"     {C_CYAN}«Мэри, запусти RMIN для проекта demo-project»{C_RESET}\n"
        "  2. ИИ-агент автоматически предложит и выполнит команду в терминале:\n"
        f"     {C_YELLOW}uv run cli.py intake --project=demo-project{C_RESET}\n\n"
        f"{C_BOLD}КАК НАЧАТЬ НОВЫЙ СОБСТВЕННЫЙ ПРОЕКТ (ПОЛНОСТЬЮ БЕЗ CLI-КОМАНД):{C_RESET}\n"
        f"  1. Просто напишите Мэри в чате вашей IDE:\n"
        f"     {C_CYAN}«Мэри, запусти RMONB для нового проекта my-project»{C_RESET} (или {C_CYAN}«RME для нового проекта my-project»{C_RESET} с нуля).\n"
        f"  2. ИИ-агент **самостоятельно создаст все папки проекта на диске, сформирует state.json и автоматически запустит** необходимые CLI-команды в вашем терминале IDE!\n"
        f"  *Вам больше не нужно вручную писать ни одной команды в консоли — просто подтверждайте автозапуск в чате IDE!*{C_RESET}\n\n"
        f"{C_BOLD}ДОПОЛНИТЕЛЬНЫЕ ИНТЕГРАЦИИ:{C_RESET}\n"
    )
    
    if obsidian_enabled:
        welcome_text += "• Obsidian: Откройте папку 'vault/' в приложении Obsidian. Там вас ждет визуальная база знаний.\n"
    if notebooklm_enabled:
        welcome_text += (
            "• Google NotebookLM: Зайдите на https://notebooklm.google/, создайте новый блокнот\n"
            "  и загрузите туда файл 'notebooklm/demo-project.json' для глубокого ИИ-анализа проекта.\n"
        )
        
    welcome_text += "\nВсе подробные инструкции и сценарии лежат в папке docs/user_guide.md."
    
    print("\n")
    print_panel(welcome_text, title=" 🎉 Успешная установка! ", color_code=C_GREEN)

def main():
    # Очистка экрана для красивого начала (если поддерживается)
    if platform.system() != "Windows" and sys.stdout.isatty():
        os.system("clear")
        
    draw_banner()
    
    try:
        detect_and_bootstrap()
        check_environment()
        python_path = setup_virtualenv()
        setup_ide_integration(python_path)
        obs_enabled = setup_obsidian_integration(python_path)
        nlm_enabled = setup_notebooklm_integration()
        setup_demo_project(python_path, nlm_enabled)
        show_welcome_tour(obs_enabled, nlm_enabled)
    except KeyboardInterrupt:
        print_color("\n\n❌ Установка прервана пользователем.", C_RED)
        sys.exit(1)

if __name__ == "__main__":
    main()
