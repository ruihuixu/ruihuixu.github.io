import json, ast, re
from collections import Counter
from pathlib import Path

BASE = Path('rl-tutorial')
NAMES = {
    'ch01': 'thinking-framework', 'ch02': 'policy-gradient-ppo',
    'ch03': 'actor-critic-evolution', 'ch04': 'preference-alignment',
    'ch05': 'generative-recsys-rl', 'ch06': 'industrial-recsys-rl'
}

findings = []

# 1. JSON validity
for ch, name in NAMES.items():
    path = BASE / f'{ch}-{name}.ipynb'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            json.load(f)
    except Exception as e:
        findings.append(f'CRITICAL: {ch} JSON: {e}')

# 2. Python syntax
for ch, name in NAMES.items():
    path = BASE / f'{ch}-{name}.ipynb'
    with open(path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    for i, c in enumerate(nb['cells']):
        if c['cell_type'] == 'code':
            code = '\n'.join(c['source'])
            try:
                ast.parse(code)
            except SyntaxError as e:
                findings.append(f'SYNTAX: {ch} cell {i}: {e}')

# 3. Cell order (ch05: env before comparison)
path = BASE / 'ch05-generative-recsys-rl.ipynb'
with open(path, 'r', encoding='utf-8') as f:
    nb = json.load(f)
env_idx = -1
comp_idx = -1
for i, c in enumerate(nb['cells']):
    src = ''.join(c['source'])
    if c['cell_type'] == 'code' and 'class GenerativeRecEnv' in src:
        env_idx = i
    if c['cell_type'] == 'code' and 'evaluate_policy' in src:
        comp_idx = i
if env_idx >= 0 and comp_idx >= 0 and env_idx > comp_idx:
    findings.append(f'ORDER: ch05 env(cell{env_idx}) AFTER comparison(cell{comp_idx})')

# 4. Section numbering duplicates
for ch, name in NAMES.items():
    path = BASE / f'{ch}-{name}.ipynb'
    with open(path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    sections = []
    for c in nb['cells']:
        src = ''.join(c['source'])
        for m in re.finditer(r'##\s+(\d+\.\d+)', src):
            sections.append(m.group(1))
    dups = [n for n, c in Counter(sections).items() if c > 1]
    if dups:
        findings.append(f'SECTION: {ch} duplicate sections: {dups}')

# 5. LaTeX matching brackets
for ch, name in NAMES.items():
    path = BASE / f'{ch}-{name}.ipynb'
    with open(path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    for i, c in enumerate(nb['cells']):
        src = ''.join(c['source'])
        if c['cell_type'] == 'markdown':
            # Check $$ display math
            blocks = src.split('$$')
            if len(blocks) % 2 == 0:
                continue  # balanced
            # Check $ inline math (excluding $$ which was split above)
            # Rejoin all odd-indexed blocks (they're inside $$ ... $$)
            # Check if any odd block has unpaired $
            for j in range(1, len(blocks), 2):
                inner = blocks[j]
                inline_dollars = inner.count('$')
                if inline_dollars % 2 != 0:
                    findings.append(f'LATEX: {ch} cell {i}: unpaired $ inside display math block')
                    break
            else:
                continue
            break
            # Check remaining for inline math
            for j in range(0, len(blocks), 2):
                dollars = blocks[j].count('$')
                if dollars % 2 != 0:
                    findings.append(f'LATEX: {ch} cell {i}: unpaired inline $')
                    break

# 6. Symbol table completeness (check actual use vs table)
with open(BASE / '_symbols.md', 'r', encoding='utf-8') as f:
    stext = f.read()
for sym_name in ['gamma', 'epsilon', 'beta', 'lambda']:
    # Check if the LaTeX form appears in symbol table
    if f'${sym_name}$' not in stext and f'$\\{sym_name}$' not in stext:
        if sym_name not in stext:
            findings.append(f'SYMBOL: {sym_name} missing from table')

# 7. Q&A coverage (count <details> with answers)
expected_answers = {'ch01': 1, 'ch02': 1, 'ch03': 0, 'ch04': 0, 'ch05': 1, 'ch06': 0}
for ch, name in NAMES.items():
    path = BASE / f'{ch}-{name}.ipynb'
    with open(path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    answer_cells = 0
    total_qs = 0
    for c in nb['cells']:
        src = ''.join(c['source'])
        total_qs += len(re.findall(r'\*\*Q\d+\*\*', src))
        if '答案要点' in src:
            answer_cells += 1
    if answer_cells < expected_answers.get(ch, 0):
        findings.append(f'QA: {ch}: {answer_cells} answer-cells, expected >= {expected_answers.get(ch, 0)}')
    # Also report if zero Qs found
    if total_qs == 0:
        findings.append(f'QA: {ch}: NO interview questions found')

# 8. Required files
for f in ['_symbols.md', '_prerequisites.md', 'research-log.md', 'paper-tracker.md']:
    if not (BASE / f).exists():
        findings.append(f'FILE: missing {f}')

# 9. Notebook has both markdown AND code cells
for ch, name in NAMES.items():
    path = BASE / f'{ch}-{name}.ipynb'
    with open(path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    md = sum(1 for c in nb['cells'] if c['cell_type'] == 'markdown')
    cd = sum(1 for c in nb['cells'] if c['cell_type'] == 'code')
    if md == 0:
        findings.append(f'CONTENT: {ch}: no markdown cells')
    if cd == 0:
        findings.append(f'CONTENT: {ch}: no code cells')

# 10. Code cells have non-empty source
for ch, name in NAMES.items():
    path = BASE / f'{ch}-{name}.ipynb'
    with open(path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    for i, c in enumerate(nb['cells']):
        if c['cell_type'] == 'code':
            code = '\n'.join(c['source']).strip()
            if not code:
                findings.append(f'EMPTY: {ch} cell {i}: empty code cell')

# REPORT
print(f'LOOP CHECK: {len(findings)} finding(s)')
for f in findings:
    print(f'  {f}')
if not findings:
    print('  ZERO findings')
