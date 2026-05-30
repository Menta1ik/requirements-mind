"""A one-off script to generate an SVG screenshot of `cli.py status` for the README.

Not part of the public CLI; run by hand when updating the README:
    .venv/bin/python scripts/_make_screenshot.py

Requires the project `projects/delivery-app/` to exist and be "populated"
with demo artifacts — the correct project setup is done by the shell wrapper
that calls this script.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Import cli as a module and swap its global Console for a recording variant.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.console import Console  # noqa: E402

import cli  # noqa: E402

recording_console = Console(record=True, width=100, force_terminal=True)
cli.console = recording_console  # swap for all handle_* in cli.py

parser = argparse.ArgumentParser()
parser.add_argument("--project", required=True)
parser.add_argument("--output", required=True)
parser.add_argument("--title", default="Requirements Mind")
args = parser.parse_args()

ns = argparse.Namespace(project=args.project)
cli.handle_status(ns)

recording_console.save_svg(args.output, title=args.title)
print(f"saved → {args.output}")
