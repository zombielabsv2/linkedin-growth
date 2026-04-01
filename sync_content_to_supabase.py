"""
Sync Content to Supabase — One-time (idempotent) migration script.
=================================================================
Reads all local content and uploads to Supabase via cloud_store.

Keys used:
  - linkedin:series:{series_key}:{filename}  — parsed posts from each series file
  - linkedin:engagement_data                  — scraped_posts.json engagement data
  - linkedin:project:{project_name}           — claude_projects/*.md project docs
  - linkedin:content_state                    — content_ops_state.json status tracking
  - linkedin:series_config                    — series configuration metadata

Usage:
  Set SUPABASE_URL and SUPABASE_KEY env vars, then:
    python sync_content_to_supabase.py

  Or create .streamlit/secrets.toml with the keys.
"""

import json
import os
import re
import sys
from pathlib import Path

# Ensure we can import cloud_store from this directory
sys.path.insert(0, str(Path(__file__).resolve().parent))

from cloud_store import cloud_put, is_cloud_available


APP_DIR = Path(__file__).resolve().parent
CONTENT_DIR = APP_DIR / "content"
DATA_DIR = APP_DIR / "data"
PROJECTS_DIR = APP_DIR / "claude_projects"

SERIES_CONFIG = {
    "org_metabolism": {
        "name": "Organizational Metabolism",
        "color": "#58a6ff",
        "files": ["org_metabolism_series.md"],
        "description": "Framework for how enterprises convert AI intelligence into structural advantage. 12-chapter book plan.",
        "target_posts": 10,
    },
    "career_volume": {
        "name": "Career Volume",
        "color": "#3fb950",
        "files": ["career_volume_series.md", "career_volume_expansion.md"],
        "description": "Length x Breadth x Depth — a framework for multi-dimensional careers. 15-chapter book plan.",
        "target_posts": 15,
    },
    "life_after_ai": {
        "name": "Life After AI",
        "color": "#bc8cff",
        "files": [
            "life_after_ai_series.md",
            "life_after_ai_series_part2.md",
            "life_after_ai_series_part3.md",
        ],
        "description": "15 dimensions of human life reshaped by AI — from daily schedules to love, income to meaning. 27 posts drafted.",
        "target_posts": 27,
    },
    "shadow_and_shade": {
        "name": "Shadow and Shade",
        "color": "#f0883e",
        "files": [
            "shadow_and_shade_series.md",
            "shadow_and_shade_hard_conversations.md",
        ],
        "description": "The Honest Manager's Playbook — Good vs Nice, the daily choice every manager faces.",
        "target_posts": 15,
    },
    "awakening_assets_access": {
        "name": "Awakening, Assets & Access",
        "color": "#f778ba",
        "files": [
            "awakening_assets_access_series.md",
            "awakening_missing_stories.md",
        ],
        "description": "Lessons from an unlikely life — memoir meets philosophy. Awakening + Assets + Access = Impact.",
        "target_posts": 15,
    },
}


def parse_posts_from_md(filepath: Path) -> list:
    """Parse a series markdown file into individual posts."""
    if not filepath.exists():
        return []
    text = filepath.read_text(encoding="utf-8")
    pattern = r"^## Post (\d+)(?:/\d+)?:\s*(.+?)$"
    parts = re.split(pattern, text, flags=re.MULTILINE)
    posts = []
    i = 1
    while i + 2 <= len(parts):
        num = parts[i].strip()
        title = parts[i + 1].strip()
        body = parts[i + 2].strip()
        body = re.sub(r"\n---\s*$", "", body).strip()
        posts.append({
            "number": int(num),
            "title": title,
            "body": body,
            "series_file": filepath.name,
        })
        i += 3
    return posts


def sync_series_content():
    """Upload all series posts to Supabase."""
    total = 0
    for series_key, cfg in SERIES_CONFIG.items():
        for fname in cfg["files"]:
            fpath = CONTENT_DIR / fname
            if not fpath.exists():
                print(f"  [SKIP] {fpath} not found")
                continue

            posts = parse_posts_from_md(fpath)
            if not posts:
                # Store raw content if no posts parsed
                raw_content = fpath.read_text(encoding="utf-8")
                key = f"linkedin:series:{series_key}:{fname}"
                data = {
                    "series_key": series_key,
                    "series_name": cfg["name"],
                    "filename": fname,
                    "raw_content": raw_content,
                    "posts": [],
                    "post_count": 0,
                }
                ok = cloud_put(key, data)
                print(f"  {'OK' if ok else 'FAIL'} {key} (raw, no posts parsed)")
                total += 1 if ok else 0
                continue

            key = f"linkedin:series:{series_key}:{fname}"
            data = {
                "series_key": series_key,
                "series_name": cfg["name"],
                "filename": fname,
                "posts": posts,
                "post_count": len(posts),
            }
            ok = cloud_put(key, data)
            print(f"  {'OK' if ok else 'FAIL'} {key} ({len(posts)} posts)")
            total += 1 if ok else 0

    return total


def sync_engagement_data():
    """Upload scraped_posts.json to Supabase."""
    json_path = DATA_DIR / "scraped_posts.json"
    if not json_path.exists():
        print("  [SKIP] scraped_posts.json not found")
        return 0

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    key = "linkedin:engagement_data"
    ok = cloud_put(key, {"posts": data, "post_count": len(data)})
    print(f"  {'OK' if ok else 'FAIL'} {key} ({len(data)} posts)")
    return 1 if ok else 0


def sync_project_docs():
    """Upload claude_projects/*.md to Supabase."""
    if not PROJECTS_DIR.exists():
        print("  [SKIP] claude_projects/ not found")
        return 0

    total = 0
    for fpath in sorted(PROJECTS_DIR.glob("*.md")):
        content = fpath.read_text(encoding="utf-8")
        # Extract a clean project name from filename
        project_name = fpath.stem  # e.g., "01_organizational_metabolism"
        key = f"linkedin:project:{project_name}"
        data = {
            "filename": fpath.name,
            "project_name": project_name,
            "content": content,
            "size_bytes": len(content.encode("utf-8")),
        }
        ok = cloud_put(key, data)
        print(f"  {'OK' if ok else 'FAIL'} {key} ({len(content)} chars)")
        total += 1 if ok else 0

    return total


def sync_content_state():
    """Upload content_ops_state.json to Supabase if it exists."""
    state_path = DATA_DIR / "content_ops_state.json"
    if not state_path.exists():
        print("  [SKIP] content_ops_state.json not found — creating empty state")
        state = {"posts": {}, "drafts": {}}
    else:
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)

    key = "linkedin:content_state"
    ok = cloud_put(key, state)
    print(f"  {'OK' if ok else 'FAIL'} {key}")
    return 1 if ok else 0


def sync_series_config():
    """Upload the series config metadata."""
    key = "linkedin:series_config"
    ok = cloud_put(key, SERIES_CONFIG)
    print(f"  {'OK' if ok else 'FAIL'} {key}")
    return 1 if ok else 0


def main():
    print("=" * 60)
    print("LinkedIn Content Ops — Sync to Supabase")
    print("=" * 60)

    if not is_cloud_available():
        print("\nERROR: Supabase not configured.")
        print("Set SUPABASE_URL and SUPABASE_KEY environment variables,")
        print("or create .streamlit/secrets.toml with these keys.")
        sys.exit(1)

    print(f"\nTable: linkedin_content_store (no user_id, service key access)")
    total = 0

    print("\n--- Series Content ---")
    total += sync_series_content()

    print("\n--- Engagement Data ---")
    total += sync_engagement_data()

    print("\n--- Project Docs ---")
    total += sync_project_docs()

    print("\n--- Content State ---")
    total += sync_content_state()

    print("\n--- Series Config ---")
    total += sync_series_config()

    print(f"\n{'=' * 60}")
    print(f"Done. {total} items synced to Supabase.")
    print("=" * 60)


if __name__ == "__main__":
    main()
