# Image Reader — Qwen VL Vision Skill

Use `scripts/read_image.py` whenever you need to visually understand an image. The main model cannot process images — this tool bridges that gap via Qwen 3.7 Plus (DashScope).

## Invocation

```bash
python3 scripts/read_image.py <image_path> [options]

# The most common pattern: ask a specific question
python3 scripts/read_image.py <image> -p "your specific question about the image"
```

## When to use

- User shares a screenshot and asks what it shows
- Need to verify UI layout after making frontend changes
- Comparing two screenshots (before/after)
- Reading text/code from an image
- Understanding diagrams, charts, or architecture drawings
- Any task where visual inspection matters

## Modes (--mode / -m)

| Mode | Use case | Example |
|------|----------|---------|
| `general` | Full description, all details (default) | First look at unknown image |
| `ui` | Web/app UI analysis | Hugo page verification, component review |
| `diagram` | Architecture/flow charts | Technical diagrams, system design |
| `chart` | Data visualization | Plots, graphs, metrics |
| `photo` | Natural images | Photos, illustrations |
| `code` | Extract code from screenshot | Code review from image |
| `text` | OCR-like text extraction | Reading documents, tables |
| `diff` | Compare two images | Before/after verification |

## Key options

| Flag | Purpose |
|------|---------|
| `-p "..."` | Custom prompt (overrides --mode) |
| `--model qwen-vl-max` | Other available model |
| `--max-tokens N` | Response length (default 2000) |
| `--temperature 0.0-2.0` | Lower = more factual, higher = more creative |
| `--json` | Structured JSON output with metadata |

## Best practices

1. **Be specific in prompts**: "这个页面的导航栏有哪些菜单项？" beats "描述这张图"
2. **Match mode to task**: Use `--mode ui` for pages, `--mode code` for code screenshots
3. **Low temperature for factual tasks**: `--temperature 0.1` for "what text is on this button"
4. **Verify, don't assume**: If the model says something unclear, ask a follow-up with a more targeted prompt
5. **Multi-image for comparison**: `python3 scripts/read_image.py before.png after.png --mode diff`

## Examples

```bash
# Verify a Hugo page renders correctly
python3 scripts/read_image.py screenshot.png --mode ui \
  -p "导航栏的RL Tutorial链接在哪个位置？页面主要区域有哪些内容？"

# Read code from a screenshot  
python3 scripts/read_image.py code-sample.png --mode code

# Compare two versions
python3 scripts/read_image.py old.png new.png --mode diff

# Quick text extraction
python3 scripts/read_image.py table.png --mode text --max-tokens 500
```
