#!/usr/bin/env python3
import os
import sys
import argparse
import asyncio
from datetime import datetime

# Проверяем наличие необходимых библиотек
try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Ошибка: Библиотека 'playwright' не установлена в текущем окружении Python.", file=sys.stderr)
    print("Пожалуйста, установите её командой: pip install playwright или uv pip install playwright", file=sys.stderr)
    sys.exit(1)

try:
    from markdownify import markdownify as md
except ImportError:
    print("Ошибка: Библиотека 'markdownify' не установлена в текущем окружении Python.", file=sys.stderr)
    print("Пожалуйста, установите её командой: pip install markdownify или uv pip install markdownify", file=sys.stderr)
    sys.exit(1)

async def main():
    parser = argparse.ArgumentParser(description="Автономный импорт веб-страниц из запущенного Chrome (CDP) в Requirements Mind.")
    parser.add_argument("--project", required=True, help="Имя проекта")
    parser.add_argument("--port", type=int, default=9222, help="Порт отладки Chrome (по умолчанию 9222)")
    parser.add_argument("--query", required=True, help="Поисковый запрос для поиска вкладки (по URL или заголовку)")
    parser.add_argument("--filename", default="confluence_specs.md", help="Имя выходного файла (по умолчанию confluence_specs.md)")
    
    args = parser.parse_args()
    
    project_dir = os.path.join("projects", args.project)
    if not os.path.exists(project_dir):
        print(f"Ошибка: Директория проекта {project_dir} не найдена. Сначала инициализируйте проект.", file=sys.stderr)
        sys.exit(1)
        
    output_path = os.path.join(project_dir, "input", args.filename)
    
    print(f"Подключение к Google Chrome на порту {args.port}...")
    
    try:
        async with async_playwright() as p:
            # Подключаемся к запущенному Chrome по протоколу CDP
            try:
                browser = await p.chromium.connect_over_cdp(f"http://localhost:{args.port}")
            except Exception as e:
                print(f"Не удалось подключиться к Chrome на порту {args.port}.", file=sys.stderr)
                print("Убедитесь, что Chrome запущен с флагом --remote-debugging-port=9222", file=sys.stderr)
                print(f"Детали ошибки: {e}", file=sys.stderr)
                sys.exit(1)
                
            # Получаем все открытые контексты и страницы
            if not browser.contexts:
                print("Ошибка: В браузере нет активных контекстов.", file=sys.stderr)
                sys.exit(1)
                
            context = browser.contexts[0]
            pages = context.pages
            
            if not pages:
                print("Ошибка: В браузере нет открытых вкладок.", file=sys.stderr)
                sys.exit(1)
                
            print(f"Сканирование {len(pages)} открытых вкладок...")
            target_page = None
            
            for page in pages:
                url = page.url
                title = await page.title()
                
                # Ищем совпадение по URL или заголовку вкладки
                if args.query.lower() in url.lower() or args.query.lower() in title.lower():
                    target_page = page
                    print(f"Найдена подходящая вкладка: '{title}' ({url})")
                    break
            
            if not target_page:
                print(f"Ошибка: Вкладка, содержащая '{args.query}', не найдена.", file=sys.stderr)
                print("Открытые вкладки в вашем браузере:", file=sys.stderr)
                for page in pages:
                    print(f" - '{await page.title()}' ({page.url})", file=sys.stderr)
                sys.exit(1)
                
            print(f"Извлечение содержимого страницы...")
            # Получаем HTML-код страницы
            html_content = await target_page.content()
            title = await target_page.title()
            
            # Конвертируем HTML в Markdown
            print("Конвертация контента в Markdown...")
            # Исключаем навигацию, шапки, подвалы и скрипты, чтобы забрать только текст
            markdown_content = md(
                html_content,
                strip=['script', 'style', 'nav', 'header', 'footer', 'noscript'],
                heading_style="ATX"
            )
            
            # Добавляем заголовок с источником
            final_markdown = (
                f"# {title}\n\n"
                f"> **Источник:** [{target_page.url}]({target_page.url})\n"
                f"> **Дата импорта:** {datetime.now().isoformat()}\n\n"
                f"---\n\n"
                f"{markdown_content}"
            )
            
            # Сохраняем в input/
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(final_markdown)
                
            print(f"Успешно импортировано {len(final_markdown)} символов в файл: {output_path}")
            
    except Exception as e:
        print(f"Непредвиденная ошибка в процессе импорта: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
