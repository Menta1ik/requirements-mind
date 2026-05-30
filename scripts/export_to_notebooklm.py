#!/usr/bin/env python3
import os
import json
import argparse
import re

CURRENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS_SRC = os.path.join(CURRENT_DIR, "projects")
NOTEBOOK_DEST = os.path.join(CURRENT_DIR, "notebooklm")

def parse_document_metadata(filename: str) -> tuple:
    """Extracts the document type and version from the file name"""
    # Patterns like 'BRD-v1.md' or 'BRD-v2-final.md'
    match = re.match(r"^([A-Za-z\-]+)-v(\d+)", filename)
    if match:
        return match.group(1), match.group(2)
    return "none", "1"

def export_project_to_json(project_name: str):
    project_path = os.path.join(PROJECTS_SRC, project_name)
    dest_file = os.path.join(NOTEBOOK_DEST, f"{project_name}.json")
    
    if not os.path.exists(project_path):
        print(f"❌ Error: Project '{project_name}' not found at: {project_path}")
        return

    print(f"📦 Building the JSON export for project: {project_name}")
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
                    
                    # Build a human-readable title
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
                    print(f"  + Added file: {file} ({rel_dir})")
                except Exception as e:
                    print(f"  ❌ Error reading file {file}: {e}")

    # Write the JSON to disk
    try:
        with open(dest_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        print("====================================================")
        print(f"🎉 JSON export completed successfully!")
        print(f"   📁 File: {dest_file}")
        print(f"   Total files exported: {len(json_data)}")
        print("====================================================")
    except Exception as e:
        print(f"❌ Error writing the JSON file: {e}")

def main():
    parser = argparse.ArgumentParser(description="Prepare a single JSON export of the project for Google NotebookLM")
    parser.add_argument("--project", required=True, help="Name of the project to export")
    args = parser.parse_args()
    
    export_project_to_json(args.project)

if __name__ == "__main__":
    main()
