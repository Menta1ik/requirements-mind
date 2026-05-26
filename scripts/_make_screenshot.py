"""Одноразовый скрипт для генерации SVG-скриншота `cli.py status` для README.

Не входит в публичный CLI; запускается вручную при обновлении README:
    .venv/bin/python scripts/_make_screenshot.py

Требует, чтобы проект `projects/delivery-app/` существовал и был «наполнен»
демо-артефактами — корректную подготовку проекта делает шелл-обвязка,
которая вызывает этот скрипт.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Импортируем cli как модуль и подменяем его глобальный Console на recording-вариант.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.console import Console  # noqa: E402

import cli  # noqa: E402

recording_console = Console(record=True, width=100, force_terminal=True)
cli.console = recording_console  # подмена для всех handle_* в cli.py

parser = argparse.ArgumentParser()
parser.add_argument("--project", required=True)
parser.add_argument("--output", required=True)
parser.add_argument("--title", default="Requirements Mind")
args = parser.parse_args()

ns = argparse.Namespace(project=args.project)
cli.handle_status(ns)

recording_console.save_svg(args.output, title=args.title)
print(f"saved → {args.output}")
