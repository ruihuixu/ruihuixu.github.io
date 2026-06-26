"""Convert Jupyter notebooks to Hugo markdown for rl-tutorial section."""
import json
import os
import re
from pathlib import Path

CHAPTERS = [
    {
        "file": "ch01-thinking-framework.ipynb",
        "slug": "thinking-framework",
        "tags": ["RL", "MDP", "Policy Gradient"],
        "chapter": 1,
        "difficulty": "入门",
        "section": "基础框架",
    },
    {
        "file": "ch02-policy-gradient-ppo.ipynb",
        "slug": "policy-gradient-ppo",
        "tags": ["RL", "PPO", "GAE", "Actor-Critic"],
        "chapter": 2,
        "difficulty": "核心",
        "section": "Actor-Critic 线",
    },
    {
        "file": "ch03-actor-critic-evolution.ipynb",
        "slug": "actor-critic-evolution",
        "tags": ["RL", "GRPO", "RLOO", "TRPO"],
        "chapter": 3,
        "difficulty": "进阶",
        "section": "Actor-Critic 线",
    },
    {
        "file": "ch04-preference-alignment.ipynb",
        "slug": "preference-alignment",
        "tags": ["RL", "RLHF", "DPO", "PPO"],
        "chapter": 4,
        "difficulty": "核心",
        "section": "偏好对齐线",
    },
    {
        "file": "ch05-generative-recsys-rl.ipynb",
        "slug": "generative-recsys-rl",
        "tags": ["RL", "推荐系统", "GRPO", "生成式推荐"],
        "chapter": 5,
        "difficulty": "进阶",
        "section": "推荐交汇",
    },
    {
        "file": "ch06-industrial-recsys-rl.ipynb",
        "slug": "industrial-recsys-rl",
        "tags": ["RL", "推荐系统", "工业实践", "ByteDance"],
        "chapter": 6,
        "difficulty": "进阶",
        "section": "推荐交汇",
    },
]


def extract_title_and_desc(nb):
    """Extract title and description from first markdown cell."""
    first_md = None
    for cell in nb["cells"]:
        if cell["cell_type"] == "markdown" and cell["source"]:
            first_md = "".join(cell["source"])
            break
    if not first_md:
        return "Untitled", ""

    title = first_md.split("\n")[0].strip()
    title = re.sub(r"^#\s+", "", title)

    # Extract description from blockquote or first real paragraph
    desc = ""
    in_blockquote = False
    for line in first_md.split("\n")[1:]:
        line = line.strip()
        if line.startswith(">"):
            blockquote_part = line.lstrip("> ").strip()
            if blockquote_part:
                desc = blockquote_part[:160]
            in_blockquote = True
            break
    if not desc:
        # Take first non-empty non-heading line
        for line in first_md.split("\n")[1:]:
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith(">"):
                desc = line[:160]
                break

    # Strip markdown markup
    desc = re.sub(r"\*\*([^*]+)\*\*", r"\1", desc)
    desc = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", desc)
    # Strip LaTeX math (backslashes break YAML double-quoted strings)
    desc = re.sub(r"\$\$?[^$]+\$\$?", "", desc)
    desc = re.sub(r"\\[a-zA-Z]+", "", desc)
    # Strip characters that break YAML double-quoted strings
    desc = desc.replace('"', "'").replace("\n", " ").replace("\r", "")
    # Collapse multiple spaces
    desc = re.sub(r"\s{2,}", " ", desc).strip()
    return title, desc


def convert_cell(cell):
    """Convert a single notebook cell to markdown string."""
    source = "".join(cell["source"])

    if cell["cell_type"] == "markdown":
        return source + "\n"

    if cell["cell_type"] == "code":
        # Strip trailing whitespace from each line and wrap in python fence
        lines = source.rstrip().split("\n")
        code = "\n".join(line.rstrip() for line in lines)
        return f"```python\n{code}\n```\n"

    return ""


def convert_notebook(nb_path, out_path, ch_meta):
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    title, desc = extract_title_and_desc(nb)
    tags_str = "\n  - " + "\n  - ".join(f'"{t}"' for t in ch_meta["tags"])

    front_matter = f"""---
title: "{title}"
date: 2026-06-26T10:00:00+08:00
draft: false
slug: "{ch_meta['slug']}"
tags:{tags_str}
categories:
  - "RL Tutorial"
description: "{desc}"
chapter: {ch_meta['chapter']}
difficulty: "{ch_meta['difficulty']}"
section: "{ch_meta['section']}"
---

"""

    body_parts = []
    for cell in nb["cells"]:
        body_parts.append(convert_cell(cell))

    body = "\n".join(body_parts)

    # Add Colab link at the end
    colab_badge = f"""
---

<a href="https://colab.research.google.com/github/rayx750/rayx750.github.io/blob/main/rl-tutorial/{ch_meta['file']}" target="_blank" style="display:inline-flex;align-items:center;gap:8px;padding:8px 16px;background:#1a1a2e;border:1px solid #333;border-radius:8px;color:#ccc;text-decoration:none;font-size:14px;">
  <svg width="20" height="20" viewBox="0 0 24 24"><path fill="#F9AB00" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 15l-5-5 1.41-1.41L11 14.17l4.59-4.58L17 11l-6 6z"/></svg>
  在 Google Colab 中打开可执行版本
</a>

> **注意**：本文中的代码经过静态语法和导入验证（`ast.parse` + 导入检查），不做完整训练。完整可执行版本请在 Colab 中运行。
"""

    content = front_matter + body + colab_badge
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)

    return title, len(body)


def main():
    base = Path(__file__).parent
    out_dir = base.parent / "content" / "rl-tutorial"
    out_dir.mkdir(parents=True, exist_ok=True)

    for ch in CHAPTERS:
        nb_path = base / ch["file"]
        out_path = out_dir / f"{ch['slug']}.md"
        title, size = convert_notebook(str(nb_path), str(out_path), ch)
        print(f"  {ch['file']} → {out_path.name}  [{title}]  ({size:,} bytes)")


if __name__ == "__main__":
    main()
