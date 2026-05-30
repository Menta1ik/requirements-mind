#!/usr/bin/env python3
import os
import json
from datetime import datetime

CURRENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS_SRC = os.path.join(CURRENT_DIR, "projects")
KB_SRC = os.path.join(CURRENT_DIR, "kb")
VAULT_DEST = os.path.join(CURRENT_DIR, "vault")

def get_project_state(project_name: str) -> dict:
    """Loads the metadata from the project's state.json"""
    state_path = os.path.join(PROJECTS_SRC, project_name, "state.json")
    if os.path.exists(state_path):
        try:
            with open(state_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def inject_frontmatter(src_path: str, dest_path: str, metadata: dict):
    """Reads a markdown file, adds or updates the YAML frontmatter, writes to dest_path"""
    try:
        with open(src_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Remove the existing frontmatter, if any, to replace it with the new one
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                content = parts[2].strip()

        # Build the YAML lines
        yaml_lines = ["---"]
        for key, value in metadata.items():
            yaml_lines.append(f"{key}: {value}")
        yaml_lines.append("---")
        
        new_content = "\n".join(yaml_lines) + "\n\n" + content
        
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(new_content)
    except Exception as e:
        print(f"❌ Error injecting metadata into the file {src_path}: {e}")

def sync_kb():
    """Copies the knowledge base into the Obsidian Vault"""
    dest_dir = os.path.join(VAULT_DEST, "knowledge-base")
    os.makedirs(dest_dir, exist_ok=True)
    
    for file in os.listdir(KB_SRC):
        if file.endswith(".md"):
            src_file = os.path.join(KB_SRC, file)
            dest_file = os.path.join(dest_dir, file)
            
            # Add a basic frontmatter for Obsidian
            metadata = {
                "type": "knowledge-base-checklist",
                "sync_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            inject_frontmatter(src_file, dest_file, metadata)

def sync_projects():
    """Copies the projects and adds a YAML frontmatter with metadata"""
    if not os.path.exists(PROJECTS_SRC):
        return
        
    for project_name in os.listdir(PROJECTS_SRC):
        project_path = os.path.join(PROJECTS_SRC, project_name)
        if not os.path.isdir(project_path) or project_name.startswith("."):
            continue
            
        dest_project_path = os.path.join(VAULT_DEST, "projects", project_name)
        state = get_project_state(project_name)
        
        # Walk the project subfolders
        for root, dirs, files in os.walk(project_path):
            rel_path = os.path.relpath(root, project_path)
            dest_dir = os.path.join(dest_project_path, rel_path) if rel_path != "." else dest_project_path
            
            for file in files:
                if file.endswith(".md"):
                    src_file = os.path.join(root, file)
                    dest_file = os.path.join(dest_dir, file)
                    
                    # Build extended metadata
                    metadata = {
                        "project": project_name,
                        "file_type": rel_path if rel_path != "." else "root",
                        "sync_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    # Merge with the data from state.json
                    if state:
                        metadata["project_status"] = state.get("status", "unknown")
                        metadata["active_document"] = state.get("document", "none")
                        metadata["current_iteration"] = state.get("iteration", 1)
                        
                    inject_frontmatter(src_file, dest_file, metadata)
                    print(f"  → Synced file with metadata: {os.path.relpath(dest_file, VAULT_DEST)}")

def main():
    print("====================================================")
    print("🔄 Running the extended sync with the Obsidian Vault")
    print("====================================================")

    print("📚 Syncing the knowledge base (kb/)...")
    sync_kb()

    print("📁 Syncing the project folders with a YAML frontmatter...")
    sync_projects()

    print("====================================================")
    print("🎉 Sync with the Obsidian Vault completed successfully!")
    print("====================================================")

if __name__ == "__main__":
    main()
