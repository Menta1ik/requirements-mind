#!/usr/bin/env python3
import os
import json
from datetime import datetime

CURRENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS_SRC = os.path.join(CURRENT_DIR, "projects")
KB_SRC = os.path.join(CURRENT_DIR, "kb")
VAULT_DEST = os.path.join(CURRENT_DIR, "vault")

def get_project_state(project_name: str) -> dict:
    """Загружает метаданные из state.json проекта"""
    state_path = os.path.join(PROJECTS_SRC, project_name, "state.json")
    if os.path.exists(state_path):
        try:
            with open(state_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def inject_frontmatter(src_path: str, dest_path: str, metadata: dict):
    """Считывает markdown-файл, добавляет или обновляет YAML frontmatter, записывает в dest_path"""
    try:
        with open(src_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Удаляем существующий frontmatter, если он есть, чтобы заменить новым
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                content = parts[2].strip()
                
        # Формируем YAML строки
        yaml_lines = ["---"]
        for key, value in metadata.items():
            yaml_lines.append(f"{key}: {value}")
        yaml_lines.append("---")
        
        new_content = "\n".join(yaml_lines) + "\n\n" + content
        
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(new_content)
    except Exception as e:
        print(f"❌ Ошибка внедрения метаданных в файл {src_path}: {e}")

def sync_kb():
    """Копирует базу знаний в Obsidian Vault"""
    dest_dir = os.path.join(VAULT_DEST, "knowledge-base")
    os.makedirs(dest_dir, exist_ok=True)
    
    for file in os.listdir(KB_SRC):
        if file.endswith(".md"):
            src_file = os.path.join(KB_SRC, file)
            dest_file = os.path.join(dest_dir, file)
            
            # Добавляем базовый frontmatter для Obsidian
            metadata = {
                "type": "knowledge-base-checklist",
                "sync_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            inject_frontmatter(src_file, dest_file, metadata)

def sync_projects():
    """Копирует проекты и добавляет YAML frontmatter с метаданными"""
    if not os.path.exists(PROJECTS_SRC):
        return
        
    for project_name in os.listdir(PROJECTS_SRC):
        project_path = os.path.join(PROJECTS_SRC, project_name)
        if not os.path.isdir(project_path) or project_name.startswith("."):
            continue
            
        dest_project_path = os.path.join(VAULT_DEST, "projects", project_name)
        state = get_project_state(project_name)
        
        # Обходим подпапки проекта
        for root, dirs, files in os.walk(project_path):
            rel_path = os.path.relpath(root, project_path)
            dest_dir = os.path.join(dest_project_path, rel_path) if rel_path != "." else dest_project_path
            
            for file in files:
                if file.endswith(".md"):
                    src_file = os.path.join(root, file)
                    dest_file = os.path.join(dest_dir, file)
                    
                    # Создаем расширенные метаданные
                    metadata = {
                        "project": project_name,
                        "file_type": rel_path if rel_path != "." else "root",
                        "sync_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    # Мержим с данными из state.json
                    if state:
                        metadata["project_status"] = state.get("status", "unknown")
                        metadata["active_document"] = state.get("document", "none")
                        metadata["current_iteration"] = state.get("iteration", 1)
                        
                    inject_frontmatter(src_file, dest_file, metadata)
                    print(f"  → Синхронизирован файл с метаданными: {os.path.relpath(dest_file, VAULT_DEST)}")

def main():
    print("====================================================")
    print("🔄 Запуск расширенной синхронизации с Obsidian Vault")
    print("====================================================")
    
    print("📚 Синхронизация базы знаний (kb/)...")
    sync_kb()
    
    print("📁 Синхронизация папок проектов с YAML frontmatter...")
    sync_projects()
    
    print("====================================================")
    print("🎉 Синхронизация с Obsidian Vault завершена успешно!")
    print("====================================================")

if __name__ == "__main__":
    main()
