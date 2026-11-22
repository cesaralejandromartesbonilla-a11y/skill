import os
import glob
import re

# Simulate optimization
# Current state:
# 1. Deduplication across global and workspace
# 2. Fusions:
#    - Ponytail (6 -> 1)
#    - Superpowers workflow (12 -> 3)
#    - Asset porters (2 -> 1)
#    - Godot C# (2 -> 1)
#    - Godot Multiplayer (3 -> 1)
#    - Godot Dialogue (2 -> 1)
#    - Godot GDScript (2 -> 1)
#    - Godot Shipping/Export (3 -> 1)
# 3. Description slimming: capping descriptions to 100-120 chars

def get_unique_skills():
    paths = [
        r'C:\Users\cesar\.gemini\config\skills',
        r'C:\Users\cesar\.gemini\config\plugins\godot-prompter\skills',
        r'c:\Users\cesar\Desktop\skill\.agents\skills',
    ]
    unique = {}
    for p in paths:
        if not os.path.exists(p): continue
        for smd in glob.glob(os.path.join(p, '*', 'SKILL.md')):
            name = os.path.basename(os.path.dirname(smd))
            with open(smd, 'r', encoding='utf-8', errors='ignore') as f:
                c = f.read()
            m = re.search(r'^description:\s*(.*?)(?=\n[a-zA-Z0-9_-]+:|\n---|\Z)', c, re.MULTILINE | re.DOTALL)
            desc = m.group(1).strip() if m else ''
            if name not in unique:
                unique[name] = desc
    return unique

unique = get_unique_skills()
print(f"Current unique skills count: {len(unique)}")
current_chars = sum(len(d) for d in unique.values())
print(f"Current unique skills chars: {current_chars} (~{current_chars // 4} tokens)")

# If descriptions are trimmed to max 120 chars:
trimmed_chars = sum(min(len(d), 120) for d in unique.values())
print(f"After trimming descriptions (<= 120 chars): {trimmed_chars} chars (~{trimmed_chars // 4} tokens)")

# After fusing 25 skills into consolidated domain skills:
# E.g. Ponytail -5, Workflow -9, Godot -10 = ~24 fewer skills
fused_count = len(unique) - 24
fused_chars = fused_count * 100
print(f"After fusing redundancies ({fused_count} skills, avg 100 chars): {fused_chars} chars (~{fused_chars // 4} tokens)")
