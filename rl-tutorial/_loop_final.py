"""Final convergence check — combines structural + deep dimensions."""
import json, ast, re
from collections import Counter
from pathlib import Path

BASE = Path('rl-tutorial')
NAMES = {
    'ch01': 'thinking-framework', 'ch02': 'policy-gradient-ppo',
    'ch03': 'actor-critic-evolution', 'ch04': 'preference-alignment',
    'ch05': 'generative-recsys-rl', 'ch06': 'industrial-recsys-rl'
}
F = []

def check(cond, msg):
    if not cond:
        F.append(msg)

# === STRUCTURAL ===
for ch, name in NAMES.items():
    path = BASE / f'{ch}-{name}.ipynb'
    # JSON
    try:
        with open(path, 'r', encoding='utf-8') as f:
            nb = json.load(f)
    except Exception as e:
        F.append(f'JSON:{ch}:{e}')
        continue

    # Syntax
    for i, c in enumerate(nb['cells']):
        if c['cell_type'] == 'code':
            try:
                ast.parse('\n'.join(c['source']))
            except SyntaxError as e:
                F.append(f'SYN:{ch}:c{i}:{e}')

    # Non-empty code cells
    for i, c in enumerate(nb['cells']):
        if c['cell_type'] == 'code':
            check('\n'.join(c['source']).strip(), f'EMPTY:{ch}:c{i}')

    # Has both md and code
    md = sum(1 for c in nb['cells'] if c['cell_type'] == 'markdown')
    cd = sum(1 for c in nb['cells'] if c['cell_type'] == 'code')
    check(md > 0, f'MD:{ch}:no markdown')
    check(cd > 0, f'CD:{ch}:no code')

    # Section duplicates
    sections = []
    for c in nb['cells']:
        for m in re.finditer(r'##\s+(\d+\.\d+)', ''.join(c['source'])):
            sections.append(m.group(1))
    dups = [n for n, c in Counter(sections).items() if c > 1]
    check(not dups, f'SEC:{ch}:dup {dups}')

    # Interview questions exist
    all_text = ' '.join(''.join(c['source']) for c in nb['cells'])
    qs = len(re.findall(r'\*\*Q\d+\*\*', all_text))
    check(qs >= 3, f'Q:{ch}:only {qs} Qs')

    # Prerequisites listed (except ch01 which is first chapter)
    check('前置' in all_text, f'PREREQ:{ch}:missing prerequisites section')

# === CELL ORDER (ch05) ===
path = BASE / 'ch05-generative-recsys-rl.ipynb'
with open(path, 'r', encoding='utf-8') as f:
    nb = json.load(f)
env_pos = comp_pos = 99
for i, c in enumerate(nb['cells']):
    src = ''.join(c['source'])
    if c['cell_type'] == 'code' and 'class GenerativeRecEnv' in src:
        env_pos = i
    if c['cell_type'] == 'code' and 'evaluate_policy' in src:
        comp_pos = i
check(env_pos < comp_pos, f'ORDER:ch05:env@{env_pos} after comparison@{comp_pos}')

# === FILES ===
for f in ['_symbols.md', '_prerequisites.md', 'research-log.md', 'paper-tracker.md']:
    check((BASE / f).exists(), f'FILE:missing {f}')

# === SYMBOL TABLE ===
with open(BASE / '_symbols.md', 'r', encoding='utf-8') as f:
    stext = f.read()
for sym in ['gamma', 'epsilon', 'beta', 'lambda']:
    check(sym in stext, f'TBL:missing {sym}')

# === SIZE BALANCE ===
sizes = {}
for ch, name in NAMES.items():
    with open(BASE / f'{ch}-{name}.ipynb', 'r', encoding='utf-8') as f:
        nb = json.load(f)
    sizes[ch] = sum(len(''.join(c['source'])) for c in nb['cells'])
avg = sum(sizes.values()) / len(sizes)
for ch, sz in sizes.items():
    check(sz > avg * 0.3, f'SIZE:{ch}:{sz} too short (avg={avg:.0f})')
    check(sz < avg * 2.5, f'SIZE:{ch}:{sz} too long (avg={avg:.0f})')

# === REPORT ===
print(f'CONVERGENCE CHECK: {len(F)} finding(s)')
for f in F:
    print(f'  {f}')
if not F:
    print('  === QUALITY CONVERGED ===')
    print(f'  Ch sizes: { {ch: sizes[ch]//1000 for ch in sizes} } KB')
