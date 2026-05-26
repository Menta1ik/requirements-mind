#!/usr/bin/env python3
import os
import json
import argparse
import re

CURRENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS_SRC = os.path.join(CURRENT_DIR, "projects")
NOTEBOOK_DEST = os.path.join(CURRENT_DIR, "notebooklm")

def parse_document_metadata(filename: str) -> tuple:
    """Извлекает тип документа и версию из имени файла"""
    # Шаблоны вида 'BRD-v1.md' или 'BRD-v2-final.md'
    match = re.match(r"^([A-Za-z\-]+)-v(\d+)", filename)
    if match:
        return match.group(1), match.group(2)
    return "none", "1"

def export_project_to_json(project_name: str):
    project_path = os.path.join(PROJECTS_SRC, project_name)
    dest_file = os.path.join(NOTEBOOK_DEST, f"{project_name}.json")
    
    if not os.path.exists(project_path):
        print(f"❌ Ошибка: Проект '{project_name}' не найден по пути: {project_path}")
        return
        
    print(f"📦 Сборка экспорта в JSON для проекта: {project_name}")
    os.makedirs(NOTEBOOK_DEST, exist_ok=True)
    
    json_data = []
    
    for root, dirs, files in os.walk(project_path):
        rel_dir = os.path.relpath(root, project_path)
        
        for file in files:
            if file.endswith(".md"):
                src_file = os.path.join(root, file)
                
                try:
                    with open(src_file, "r", encoding="utf-8") as f:
                        content = f.read()
                        
                    doc_type, version = parse_document_metadata(file)
                    
                    # Определяем человекочитаемый заголовок
                    title = f"{doc_type} — {project_name} v{version}" if doc_type != "none" else f"{file.replace('.md', '')} — {project_name}"
                    
                    entry = {
                        "title": title,
                        "content": content,
                        "source": os.path.relpath(src_file, CURRENT_DIR),
                        "project": project_name,
                        "type": rel_dir if rel_dir != "." else "root",
                        "document": doc_type,
                        "version": version
                    }
                    json_data.append(entry)
                    print(f"  + Добавлен файл: {file} ({rel_dir})")
                except Exception as e:
                    print(f"  ❌ Ошибка чтения файла {file}: {e}")
                    
    # Записываем JSON на диск
    try:
        with open(dest_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        print("====================================================")
        print(f"🎉 Экспорт в JSON успешно завершен!")
        print(f"   📁 Файл: {dest_file}")
        print(f"   Всего экспортировано файлов: {len(json_data)}")
        print("====================================================")
    except Exception as e:
        print(f"❌ Ошибка записи JSON файла: {e}")

def main():
    parser = argparse.ArgumentParser(description="Подготовка единого JSON-экспорта проекта для Google NotebookLM")
    parser.add_argument("--project", required=True, help="Название проекта для экспорта")
    args = parser.parse_args()
    
    export_project_to_json(args.project)

if __name__ == "__main__":
    main()
