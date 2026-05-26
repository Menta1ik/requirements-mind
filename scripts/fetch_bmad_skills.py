#!/usr/bin/env python3
import os
import shutil
import sys

# Пути к репозиториям
BMAD_REPO_PATH = "/Users/macbook/Projects/BMAD-METHOD"
CURRENT_PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST_SKILLS_PATH = os.path.join(CURRENT_PROJECT_PATH, "skills", "bmad")

# Полный маппинг 17 навыков из спецификации
SKILLS_MAPPING = {
    # Из bmm-skills/1-analysis/
    "bmad-agent-analyst": "src/bmm-skills/1-analysis/bmad-agent-analyst",
    "bmad-agent-tech-writer": "src/bmm-skills/1-analysis/bmad-agent-tech-writer",
    "research": "src/bmm-skills/1-analysis/research",
    
    # Из bmm-skills/2-plan-workflows/
    "bmad-agent-pm": "src/bmm-skills/2-plan-workflows/bmad-agent-pm",
    "bmad-create-prd": "src/bmm-skills/2-plan-workflows/bmad-create-prd",
    "bmad-edit-prd": "src/bmm-skills/2-plan-workflows/bmad-edit-prd",
    "bmad-validate-prd": "src/bmm-skills/2-plan-workflows/bmad-validate-prd",
    "bmad-prd": "src/bmm-skills/2-plan-workflows/bmad-prd",
    
    # Из core-skills/
    "bmad-party-mode": "src/core-skills/bmad-party-mode",
    "bmad-advanced-elicitation": "src/core-skills/bmad-advanced-elicitation",
    "bmad-spec": "src/core-skills/bmad-spec",
    "bmad-review-adversarial-general": "src/core-skills/bmad-review-adversarial-general",
    "bmad-review-edge-case-hunter": "src/core-skills/bmad-review-edge-case-hunter",
    "bmad-editorial-review-prose": "src/core-skills/bmad-editorial-review-prose",
    "bmad-editorial-review-structure": "src/core-skills/bmad-editorial-review-structure",
    "bmad-index-docs": "src/core-skills/bmad-index-docs",
    "bmad-brainstorming": "src/core-skills/bmad-brainstorming"
}

def main():
    print("====================================================")
    print("🚀 Запуск скрипта импорта 17 навыков из BMAD-METHOD")
    print("====================================================")

    # 1. Проверяем наличие репозитория BMAD-METHOD
    if not os.path.exists(BMAD_REPO_PATH):
        print(f"❌ Ошибка: Локальный репозиторий BMAD-METHOD не найден по пути: {BMAD_REPO_PATH}")
        print("Пожалуйста, убедитесь, что репозиторий клонирован правильно.")
        sys.exit(1)

    print(f"✅ Найден репозиторий BMAD-METHOD: {BMAD_REPO_PATH}")
    print(f"📁 Целевая папка для навыков: {DEST_SKILLS_PATH}")
    
    # Создаем целевую директорию, если она не существует
    os.makedirs(DEST_SKILLS_PATH, exist_ok=True)

    # 2. Копируем навыки согласно маппингу
    success_count = 0
    for skill_name, rel_path in SKILLS_MAPPING.items():
        src_path = os.path.join(BMAD_REPO_PATH, rel_path)
        dest_path = os.path.join(DEST_SKILLS_PATH, skill_name)

        if not os.path.exists(src_path):
            print(f"⚠️  Ошибка: Исходная папка для навыка '{skill_name}' не найдена по пути: {src_path}")
            continue

        # Если целевая папка уже существует, удаляем её перед копированием
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)

        try:
            shutil.copytree(src_path, dest_path)
            print(f"✅ Успешно скопирован навык: {skill_name} -> skills/bmad/{skill_name}")
            success_count += 1
        except Exception as e:
            print(f"❌ Ошибка при копировании навыка {skill_name}: {e}")

    print("====================================================")
    print(f"🎉 Скрипт завершил работу. Успешно импортировано навыков: {success_count}/{len(SKILLS_MAPPING)}")
    print("====================================================")

if __name__ == "__main__":
    main()
