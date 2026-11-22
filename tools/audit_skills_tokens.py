import os
import glob
import re
from collections import defaultdict

paths = [
    r'c:\Users\cesar\Desktop\skill\.agents\skills',
    r'c:\Users\cesar\Desktop\skill\skills',
    r'C:\Users\cesar\.gemini\config\plugins\global-mcp-skills-hub\skills',
    r'C:\Users\cesar\.gemini\config\plugins\godot-prompter\skills',
    r'C:\Users\cesar\.gemini\config\skills'
]

skills = []
for p in paths:
    if not os.path.exists(p):
        continue
    for skill_md in glob.glob(os.path.join(p, '*', 'SKILL.md')):
        with open(skill_md, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
        desc_match = re.search(r'^description:\s*(.*?)(?=\n[a-zA-Z0-9_-]+:|\n---|\Z)', content, re.MULTILINE | re.DOTALL)
        name = name_match.group(1).strip() if name_match else os.path.basename(os.path.dirname(skill_md))
        desc = desc_match.group(1).strip() if desc_match else ''
        skills.append({
            'source_dir': p,
            'skill_dir': os.path.basename(os.path.dirname(skill_md)),
            'name': name,
            'desc_len': len(desc),
            'desc_est_tokens': len(desc) // 4,
            'total_len': len(content),
            'total_tokens': len(content) // 4,
            'desc': desc
        })

print(f"Total skills scanned across all directories: {len(skills)}")
total_desc_chars = sum(s['desc_len'] for s in skills)
total_desc_tokens = sum(s['desc_est_tokens'] for s in skills)
print(f"Total description characters injected: {total_desc_chars}")
print(f"Total estimated description tokens in system prompt: {total_desc_tokens}")

by_name = defaultdict(list)
for s in skills:
    by_name[s['name']].append(s)

print(f"\nUnique skill names: {len(by_name)}")
dupes = {k: v for k, v in by_name.items() if len(v) > 1}
print(f"Duplicated skills count: {len(dupes)}")
for k, v in dupes.items():
    locs = [os.path.basename(x['source_dir']) for x in v]
    print(f"  - {k} ({len(v)} copies in {locs})")

skills_sorted = sorted(skills, key=lambda x: x['desc_len'], reverse=True)
print("\nTop 15 Longest Descriptions (Top Token Consumers in System Prompt):")
seen = set()
count = 0
for s in skills_sorted:
    if s['name'] in seen:
        continue
    seen.add(s['name'])
    count += 1
    print(f"{count}. {s['name']}: {s['desc_len']} chars (~{s['desc_est_tokens']} tokens)")
    preview = s['desc'].replace('\n', ' ')[:120]
    print(f"   Preview: {preview}...")
    if count >= 15:
        break
