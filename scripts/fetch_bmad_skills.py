#!/usr/bin/env python3
import os
import shutil
import sys

# Repository paths
BMAD_REPO_PATH = "/Users/macbook/Projects/BMAD-METHOD"
CURRENT_PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST_SKILLS_PATH = os.path.join(CURRENT_PROJECT_PATH, "skills", "bmad")

# The full mapping of the 17 skills from the specification
SKILLS_MAPPING = {
    # From bmm-skills/1-analysis/
    "bmad-agent-analyst": "src/bmm-skills/1-analysis/bmad-agent-analyst",
    "bmad-agent-tech-writer": "src/bmm-skills/1-analysis/bmad-agent-tech-writer",
    "research": "src/bmm-skills/1-analysis/research",

    # From bmm-skills/2-plan-workflows/
    "bmad-agent-pm": "src/bmm-skills/2-plan-workflows/bmad-agent-pm",
    "bmad-create-prd": "src/bmm-skills/2-plan-workflows/bmad-create-prd",
    "bmad-edit-prd": "src/bmm-skills/2-plan-workflows/bmad-edit-prd",
    "bmad-validate-prd": "src/bmm-skills/2-plan-workflows/bmad-validate-prd",
    "bmad-prd": "src/bmm-skills/2-plan-workflows/bmad-prd",

    # From core-skills/
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
    print("🚀 Running the script to import the 17 skills from BMAD-METHOD")
    print("====================================================")

    # 1. Check that the BMAD-METHOD repository is present
    if not os.path.exists(BMAD_REPO_PATH):
        print(f"❌ Error: The local BMAD-METHOD repository was not found at: {BMAD_REPO_PATH}")
        print("Please make sure the repository is cloned correctly.")
        sys.exit(1)

    print(f"✅ Found the BMAD-METHOD repository: {BMAD_REPO_PATH}")
    print(f"📁 Target folder for the skills: {DEST_SKILLS_PATH}")

    # Create the target directory if it does not exist
    os.makedirs(DEST_SKILLS_PATH, exist_ok=True)

    # 2. Copy the skills according to the mapping
    success_count = 0
    for skill_name, rel_path in SKILLS_MAPPING.items():
        src_path = os.path.join(BMAD_REPO_PATH, rel_path)
        dest_path = os.path.join(DEST_SKILLS_PATH, skill_name)

        if not os.path.exists(src_path):
            print(f"⚠️  Error: The source folder for the skill '{skill_name}' was not found at: {src_path}")
            continue

        # If the target folder already exists, remove it before copying
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)

        try:
            shutil.copytree(src_path, dest_path)
            print(f"✅ Successfully copied the skill: {skill_name} -> skills/bmad/{skill_name}")
            success_count += 1
        except Exception as e:
            print(f"❌ Error copying the skill {skill_name}: {e}")

    print("====================================================")
    print(f"🎉 The script has finished. Skills successfully imported: {success_count}/{len(SKILLS_MAPPING)}")
    print("====================================================")

if __name__ == "__main__":
    main()
