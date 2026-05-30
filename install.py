#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import subprocess
import platform

# Terminal color definitions
C_CYAN = "\033[96m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_RED = "\033[91m"
C_BOLD = "\033[1m"
C_RESET = "\033[0m"

def print_color(text, color_code):
    """Prints text with highlighting if the terminal supports colors."""
    # Check whether the terminal supports colors
    if sys.stdout.isatty():
        print(f"{color_code}{text}{C_RESET}")
    else:
        print(text)

def print_panel(text, title="", color_code=C_GREEN):
    """Draws a nice terminal panel (box) around the text."""
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
    """Draws the welcome banner."""
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
        "Welcome to Requirements Mind!\n"
        "Interactive installer for your local working environment.\n\n"
        "This script will prepare the Python dependencies, link the AI skills to your IDE,\n"
        "and set up the Obsidian Vault knowledge base and Google NotebookLM.",
        title=" Requirements Mind v2.0 Setup ",
        color_code=C_CYAN
    )

def detect_and_bootstrap():
    """Phase 0: Checks for core files in the current folder. If absent, downloads the distribution from GitHub."""
    required_files = ["cli.py", "requirements.txt"]
    required_folders = ["skills", "kb"]

    is_installed = all(os.path.exists(f) for f in required_files) and \
                   all(os.path.exists(d) and os.path.isdir(d) for d in required_folders)

    if is_installed:
        return

    print_color("\n⚠️  Warning: no Requirements Mind core files were found in the current folder.", C_YELLOW)
    print_color("🚀 Starting a from-scratch global bootstrap installation!", C_CYAN)

    ans = input("Download and unpack the distribution into the current folder? [Y/n]: ").strip().lower()
    if ans not in ('', 'y', 'yes'):
        print_color("❌ Installation cancelled by user.", C_RED)
        sys.exit(0)

    url = "https://github.com/Menta1ik/requirements-mind/archive/refs/heads/main.zip"
    print(f"  • Downloading the distribution from {url} ... ", end="", flush=True)

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
        print_color("ERROR", C_RED)
        print(f"Failed to download the distribution: {e}")
        sys.exit(1)

    print("  • Unpacking the distribution files ... ", end="", flush=True)
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
                raise Exception("Could not find the distribution root folder inside the archive.")

            dist_folder_path = os.path.join(temp_dir, dist_folder_name)

            # Copy all contents into the current folder
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
            "All Requirements Mind core files have been downloaded successfully!\n"
            "Moving on to interactive environment setup.",
            title=" Download complete ",
            color_code=C_GREEN
        )
    except Exception as e:
        print_color("ERROR", C_RED)
        print(f"Failed to unpack the distribution: {e}")
        sys.exit(1)

def check_environment():
    """Step 1: Check the base environment."""
    print_color("\n🔍 Step 1: Checking the base system environment...", C_BOLD)

    # 1. Check the Python version
    py_version = sys.version_info
    print(f"  • Python version: {py_version.major}.{py_version.minor}.{py_version.micro} ... ", end="")
    if py_version.major < 3 or (py_version.major == 3 and py_version.minor < 10):
        print_color("UNSUPPORTED", C_RED)
        print_panel(
            "Error: Requirements Mind requires Python 3.10 or higher.\n"
            "Please upgrade Python and run the installer again.",
            title=" Python error ",
            color_code=C_RED
        )
        sys.exit(1)
    else:
        print_color("OK", C_GREEN)

    # 2. Check Git
    print("  • Checking Git ... ", end="")
    git_path = shutil.which("git")
    if not git_path:
        print_color("NOT FOUND", C_RED)
        print_panel(
            "Warning: Git was not detected on your system.\n"
            "Requirements Mind uses Git for collaboration between multiple analysts\n"
            "and for versioning requirements.\n\n"
            "We recommend installing Git: https://git-scm.com/",
            title=" Git warning ",
            color_code=C_YELLOW
        )
    else:
        try:
            res = subprocess.run(["git", "--version"], capture_output=True, text=True)
            print_color(f"OK ({res.stdout.strip()})", C_GREEN)
        except Exception:
            print_color("OK", C_GREEN)

def setup_virtualenv():
    """Step 2: Create the virtual environment and install dependencies."""
    print_color("\n📦 Step 2: Setting up the virtual environment and dependencies...", C_BOLD)

    # 1. Check for uv
    uv_path = shutil.which("uv")
    use_uv = False

    if uv_path:
        print_color("  • uv detected! Installation will be 10x faster.", C_GREEN)
        use_uv = True
    else:
        ans = input(f"  • [Optional] Install 'uv' for ultra-fast dependency handling? [y/N]: ").strip().lower()
        if ans in ('y', 'yes'):
            print("  • Attempting to install uv...")
            try:
                # Try to install uv globally via pip
                subprocess.run([sys.executable, "-m", "pip", "install", "uv"], check=True)
                uv_path = shutil.which("uv")
                if uv_path:
                    print_color("  • 'uv' installed successfully!", C_GREEN)
                    use_uv = True
            except Exception:
                print_color("  • Could not install uv. Falling back to standard pip.", C_YELLOW)

    # 2. Create the virtual environment
    venv_dir = ".venv"
    if not os.path.exists(venv_dir):
        print(f"  • Creating the virtual environment in '{venv_dir}' ... ", end="")
        try:
            if use_uv:
                subprocess.run(["uv", "venv", venv_dir], check=True, capture_output=True)
            else:
                subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
            print_color("OK", C_GREEN)
        except Exception as e:
            print_color("ERROR", C_RED)
            print(f"Failed to create venv: {e}")
            sys.exit(1)
    else:
        print_color(f"  • Virtual environment '{venv_dir}' already exists. Skipping creation.", C_CYAN)

    # 3. Determine the paths to the venv executables
    if platform.system() == "Windows":
        pip_path = os.path.join(venv_dir, "Scripts", "pip")
        python_path = os.path.join(venv_dir, "Scripts", "python")
    else:
        pip_path = os.path.join(venv_dir, "bin", "pip")
        python_path = os.path.join(venv_dir, "bin", "python")

    # 4. Install dependencies
    print("  • Installing the required libraries (Rich, Pydantic, Playwright)... ")
    try:
        if use_uv:
            subprocess.run(["uv", "pip", "install", "-r", "requirements.txt"], check=True)
        else:
            subprocess.run([pip_path, "install", "-U", "pip"], check=True, capture_output=True)
            subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        print_color("  • All dependencies installed successfully!", C_GREEN)
    except Exception as e:
        print_color(f"  • Error installing dependencies: {e}", C_RED)
        sys.exit(1)

    return python_path

def setup_ide_integration(python_path):
    """Step 3: Set up the AI skills in the IDE."""
    print_color("\n💻 Step 3: Integrating IDE AI assistants...", C_BOLD)
    print(
        "Requirements Mind version 2.0 uses IDE-native AI assistants.\n"
        "We will link our AI skills to the service folders of your development environments.\n"
    )

    print("Choose your AI assistant:")
    print("  [1] Cursor / VS Code + Copilot  (recommended)")
    print("  [2] Claude Code")
    print("  [3] Google Antigravity")
    print("  [4] OpenAI Codex CLI")
    print("  [5] All of the above")
    print("  [6] Skip this step")

    choice = input(f"\nEnter your choice [1-6, default 1]: ").strip()
    if not choice:
        choice = "1"

    if choice == "6":
        # Hint with the correct Python name for the current OS
        py_hint = "python" if platform.system() == "Windows" else "python3"
        print_color(f"  • Step skipped. You can link them later manually: `{py_hint} cli.py setup-ide`.", C_YELLOW)
        return

    print("  • Linking the skills into the IDE...")
    try:
        # Call the built-in handler in cli.py via the venv python
        subprocess.run([python_path, "cli.py", "setup-ide"], check=True)
    except Exception as e:
        print_color(f"  • Error setting up the IDE: {e}", C_RED)

def setup_obsidian_integration(python_path):
    """Step 4: Set up Obsidian."""
    print_color("\n📓 Step 4: Setting up visualization in Obsidian...", C_BOLD)
    ans = input("Set up an Obsidian Vault for an interactive requirements graph? [Y/n]: ").strip().lower()
    if ans in ('', 'y', 'yes'):
        vault_dir = "vault"
        os.makedirs(vault_dir, exist_ok=True)
        print_color(f"  • Local directory '{vault_dir}/' prepared.", C_GREEN)
        print("  • Syncing files with Obsidian...")
        try:
            subprocess.run([python_path, "cli.py", "sync-vault"], check=True)
            print_color("  • Synced successfully!", C_GREEN)
        except Exception as e:
            print_color(f"  • Sync failed: {e}", C_RED)
        return True
    else:
        print_color("  • Step skipped.", C_YELLOW)
        return False

def setup_notebooklm_integration():
    """Step 5: Set up Google NotebookLM."""
    print_color("\n📤 Step 5: Setting up Google NotebookLM...", C_BOLD)
    ans = input("Initialize the export folder for Google NotebookLM? [Y/n]: ").strip().lower()
    if ans in ('', 'y', 'yes'):
        os.makedirs("notebooklm", exist_ok=True)
        print_color("  • Local directory 'notebooklm/' created successfully.", C_GREEN)
        return True
    else:
        print_color("  • Step skipped.", C_YELLOW)
        return False

def setup_demo_project(python_path, notebooklm_enabled):
    """Step 6: Initialize the demo project."""
    print_color("\n🚀 Step 6: Creating the demo project...", C_BOLD)
    ans = input("Deploy a ready-made demo project for a quick tour? [Y/n]: ").strip().lower()
    if ans in ('', 'y', 'yes'):
        project_name = "demo-project"
        print(f"  • Initializing the project '{project_name}' ... ", end="")
        try:
            subprocess.run([python_path, "cli.py", "init", "--project", project_name], check=True, capture_output=True)
            subprocess.run([python_path, "cli.py", "onboard", "--project", project_name], check=True, capture_output=True)
            print_color("OK", C_GREEN)
        except Exception as e:
            print_color("ERROR", C_RED)
            print(f"Failed to initialize the demo project: {e}")
            return

        # Write the demo raw requirements
        input_req_file = f"projects/{project_name}/input/requirements.md"
        demo_requirements = """# Demo requirements: "QuickBite" food-delivery service

## 1. Concept description
We want to launch a mobile app and a website for ultra-fast delivery of ready-made meals from our dark kitchens.
Delivery time must not exceed 20 minutes from the moment of ordering.

## 2. Core functionality (MVP)
* User authentication by phone number and a one-time SMS code.
* Interactive map for choosing the delivery address (with delivery-zone coverage check).
* Menu catalog with the ability to add dishes to the cart and track allergens.
* Payment by bank card or via instant bank transfer.
* Real-time courier tracking on the map.

## 3. Non-functional requirements
* The app must work even on a weak 3G connection.
* High fault tolerance during peak hours (12:00–14:00 and 19:00–21:00).
"""
        try:
            with open(input_req_file, "w", encoding="utf-8") as f:
                f.write(demo_requirements)
            print_color(f"  • Demo requirements written to {input_req_file}", C_GREEN)
        except Exception as e:
            print(f"  • Failed to write the demo requirements: {e}")

        # If NotebookLM is enabled, generate the demo export right away
        if notebooklm_enabled:
            print("  • Auto-generating the demo export for Google NotebookLM...")
            try:
                subprocess.run([python_path, "cli.py", "export-notebooklm", "--project", project_name], check=True, capture_output=True)
                print_color(f"  • Export file created at: notebooklm/{project_name}.json", C_GREEN)
            except Exception as e:
                print(f"  • Error generating the demo export for NotebookLM: {e}")
        return True
    else:
        print_color("  • Step skipped.", C_YELLOW)
        return False

def show_welcome_tour(obsidian_enabled, notebooklm_enabled):
    """Prints the cheat sheet and congratulations."""
    welcome_text = (
        "Congratulations! Requirements Mind is fully installed and configured!\n\n"
        f"{C_BOLD}QUICK START FOR THE ANALYST:{C_RESET}\n"
        "• For the demo project (demo-project):\n"
        "  1. Open your IDE's AI assistant chat and start Intake:\n"
        f"     {C_CYAN}\"Mary, run RMIN for the demo-project project\"{C_RESET}\n"
        "  2. The AI agent will automatically propose and run the command in the terminal:\n"
        f"     {C_YELLOW}uv run cli.py intake --project=demo-project{C_RESET}\n\n"
        f"{C_BOLD}HOW TO START A NEW PROJECT OF YOUR OWN (FULLY WITHOUT CLI COMMANDS):{C_RESET}\n"
        f"  1. Just tell Mary in your IDE's chat:\n"
        f"     {C_CYAN}\"Mary, run RMONB for a new project my-project\"{C_RESET} (or {C_CYAN}\"RME for a new project my-project\"{C_RESET} from scratch).\n"
        f"  2. The AI agent will **create all the project folders on disk on its own, build state.json, and automatically run** the necessary CLI commands in your IDE terminal!\n"
        f"  *You no longer need to type a single command in the console by hand — just confirm the auto-run in the IDE chat!*{C_RESET}\n\n"
        f"{C_BOLD}ADDITIONAL INTEGRATIONS:{C_RESET}\n"
    )

    if obsidian_enabled:
        welcome_text += "• Obsidian: Open the 'vault/' folder in the Obsidian app. A visual knowledge base awaits you there.\n"
    if notebooklm_enabled:
        welcome_text += (
            "• Google NotebookLM: Go to https://notebooklm.google/, create a new notebook,\n"
            "  and upload the file 'notebooklm/demo-project.json' there for deep AI analysis of the project.\n"
        )

    welcome_text += "\nAll detailed instructions and scenarios live in the docs/user_guide.md folder."

    print("\n")
    print_panel(welcome_text, title=" 🎉 Installation successful! ", color_code=C_GREEN)

def main():
    # Clear the screen for a clean start (if supported)
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
        print_color("\n\n❌ Installation interrupted by user.", C_RED)
        sys.exit(1)

if __name__ == "__main__":
    main()
