#!/usr/bin/env python3
"""
search_vault.py - Lightweight search and indexer for Algo-Vault.
Can be executed by humans or AI agents to retrieve suitable algorithms.

Usage:
  python3 search_vault.py                    # List all cards
  python3 search_vault.py "转录因子"          # Keyword search
  python3 search_vault.py --task "扰动预测"   # Task search
  python3 search_vault.py --json             # Output structured JSON
"""

import sys
import re
import json
from pathlib import Path

VAULT_DIR = Path(__file__).resolve().parent.parent

def parse_frontmatter(file_path: Path):
    content = file_path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return None
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    raw_yaml = parts[1]
    
    # Simple lightweight YAML parser to avoid external PyYAML dependency
    data = {"file_path": str(file_path.relative_to(VAULT_DIR))}
    for line in raw_yaml.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if val.startswith("[") and val.endswith("]"):
                # Parse list
                items = [x.strip().strip('"').strip("'") for x in val[1:-1].split(",") if x.strip()]
                data[key] = items
            elif val:
                data[key] = val
            else:
                data[key] = []
        elif line.startswith("-") and key in data and isinstance(data[key], list):
            item = line[1:].strip().strip('"').strip("'")
            data[key].append(item)
    return data, parts[2].strip()

def get_all_cards():
    cards = []
    for md_file in VAULT_DIR.rglob("*.md"):
        if "templates" in md_file.parts or md_file.name.lower() == "readme.md":
            continue
        res = parse_frontmatter(md_file)
        if res:
            meta, body = res
            cards.append((meta, body))
    return cards

def main():
    args = sys.argv[1:]
    json_output = "--json" in args
    args = [a for a in args if a != "--json"]
    
    query = " ".join(args).lower() if args else ""
    cards = get_all_cards()
    
    matched = []
    for meta, body in cards:
        searchable_text = (
            str(meta.get("name", "")) + " " +
            " ".join(meta.get("category", [])) + " " +
            " ".join(meta.get("target_problems", [])) + " " +
            " ".join(meta.get("data_modalities", [])) + " " +
            body[:1500]
        ).lower()
        
        if not query or query in searchable_text:
            matched.append(meta)
            
    if json_output:
        print(json.dumps(matched, ensure_ascii=False, indent=2))
    else:
        print(f"=== 🔍 Algo-Vault 检索结果 (共找到 {len(matched)} 项) ===\n")
        for m in matched:
            print(f"📌 【{m.get('name', '未命名')}】 ({m.get('file_path')})")
            print(f"   • 分类: {', '.join(m.get('category', []))}")
            print(f"   • 解决问题: {', '.join(m.get('target_problems', []))}")
            print(f"   • 数据模态: {', '.join(m.get('data_modalities', []))}")
            print(f"   • 来源: {m.get('repo_url', 'N/A')}\n")

if __name__ == "__main__":
    main()
