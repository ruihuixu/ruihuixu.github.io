#!/usr/bin/env python3
"""
Image reader powered by Qwen VL (DashScope).

Flexible CLI for describing images — screenshots, diagrams, charts, photos, etc.
Works with Claude Code via Bash; API key from DASHSCOPE_API_KEY env.

Usage:
    # Basic: describe a single image
    python scripts/read_image.py screenshot.png

    # Custom prompt
    python scripts/read_image.py chart.png -p "这个图表的X轴和Y轴分别是什么？趋势如何？"

    # Preset mode
    python scripts/read_image.py diagram.jpg --mode diagram
    python scripts/read_image.py photo.jpg   --mode photo
    python scripts/read_image.py page.png    --mode ui

    # Multiple images (compare)
    python scripts/read_image.py before.png after.png -p "两张图有什么不同？"

    # Adjust output
    python scripts/read_image.py img.png --model qwen-vl-plus --max-tokens 500 --temperature 0.1

    # Structured output
    python scripts/read_image.py img.png --json

Modes (--mode):
    general   - Full description with all details (default)
    ui        - Focus on UI layout, components, styling
    diagram   - Focus on diagram structure, relationships, labels
    chart     - Focus on data, axes, trends
    photo     - Focus on visual content, objects, scene
    code      - Focus on extracting/reading code from screenshot
    text      - Focus on extracting text content (OCR-like)
    diff      - Compare two images and highlight differences
"""

import argparse
import base64
import json
import os
import sys
from typing import Optional

from openai import OpenAI

BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODELS = {
    "qwen3.7-plus": "qwen3.7-plus",
    "qwen-vl-max": "qwen-vl-max",
    "qwen-vl-plus": "qwen-vl-plus",
}
DEFAULT_MODEL = "qwen3.7-plus"

MIME_MAP = {
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".webp": "image/webp", ".gif": "image/gif", ".bmp": "image/bmp",
}

PRESET_PROMPTS = {
    "general": (
        "请详细描述这张图片的全部内容，包括：整体布局、所有可见文字、图表/数据、"
        "UI元素（按钮/菜单/输入框等）、颜色方案、视觉层次。如果是网页或应用截图，"
        "请逐区域描述页面结构和导航。不要遗漏任何细节。"
    ),
    "ui": (
        "这是一张 UI/网页截图。请分析：1) 页面整体布局（header/sidebar/main/footer）；"
        "2) 导航结构和菜单项；3) 主要组件（按钮、表单、卡片、表格等）及其位置；"
        "4) 颜色方案和视觉风格；5) 文字内容和层级关系。"
    ),
    "diagram": (
        "这是一张图表/示意图。请分析：1) 图表类型（流程图/架构图/关系图等）；"
        "2) 各个节点/组件的名称和含义；3) 节点之间的连接关系和方向；"
        "4) 分组或层次结构；5) 所有标注文字。"
    ),
    "chart": (
        "这是一张数据图表。请分析：1) 图表类型（折线图/柱状图/饼图等）；"
        "2) X轴和Y轴的含义和刻度；3) 数据系列和趋势；4) 图例和标签；"
        "5) 关键数据点和异常值。"
    ),
    "photo": (
        "请描述这张照片/图片的视觉内容：主体对象、场景、颜色、光线、构图、"
        "氛围，以及任何值得注意的细节。"
    ),
    "code": (
        "请提取并完整输出这张截图中所有的代码，保持原有缩进和格式。"
        "如果代码有语法高亮，请忽略颜色，只关注代码文本本身。"
    ),
    "text": (
        "请提取这张图片中的所有文字内容，保持原有的结构和层级关系。"
        "对于表格，保持行列结构。对于列表，保持项目符号。"
    ),
    "diff": (
        "请仔细比较这两张图片，列出所有不同之处。包括：布局变化、新增/删除的元素、"
        "文字变更、颜色变化、位置移动等。差异较多的区域请重点标注。"
    ),
}


def encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_mime_type(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    return MIME_MAP.get(ext, "image/png")


def build_messages(
    images: list[str],
    prompt: str,
    system: Optional[str] = None,
) -> list[dict]:
    """Build chat messages with one or more images."""
    content = []
    for img_path in images:
        mime = get_mime_type(img_path)
        b64 = encode_image(img_path)
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:{mime};base64,{b64}"},
        })
    content.append({"type": "text", "text": prompt})

    messages = [{"role": "user", "content": content}]
    if system:
        messages.insert(0, {"role": "system", "content": system})

    return messages


def describe_images(
    images: list[str],
    prompt: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 2000,
    temperature: float = 0.7,
    system: Optional[str] = None,
) -> str:
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        print("Error: DASHSCOPE_API_KEY not set in environment", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key, base_url=BASE_URL)
    messages = build_messages(images, prompt, system)

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    return response.choices[0].message.content


def main():
    parser = argparse.ArgumentParser(
        description="Image reader — Qwen VL via DashScope",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("images", nargs="+", help="One or more image file paths")
    parser.add_argument("--prompt", "-p", default=None,
                        help="Custom prompt (overrides --mode)")
    parser.add_argument("--mode", "-m", choices=list(PRESET_PROMPTS), default="general",
                        help="Preset prompt mode (default: general)")
    parser.add_argument("--model", choices=list(MODELS), default=DEFAULT_MODEL,
                        help="Model to use (default: qwen-vl-max)")
    parser.add_argument("--max-tokens", "-t", type=int, default=2000,
                        help="Max output tokens (default: 2000)")
    parser.add_argument("--temperature", type=float, default=0.7,
                        help="Response creativity 0.0-2.0 (default: 0.7)")
    parser.add_argument("--system", "-s", default=None,
                        help="System message for model context")
    parser.add_argument("--json", dest="json_output", action="store_true",
                        help="Output as JSON with metadata")
    parser.add_argument("--output", "-o", default=None,
                        help="Write output to file (UTF-8)")

    args = parser.parse_args()

    for img in args.images:
        if not os.path.exists(img):
            print(f"Error: file not found: {img}", file=sys.stderr)
            sys.exit(1)

    prompt = args.prompt or PRESET_PROMPTS[args.mode]

    result = describe_images(
        images=args.images,
        prompt=prompt,
        model=args.model,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        system=args.system,
    )

    if args.json_output:
        output = {
            "model": args.model,
            "images": args.images,
            "mode": args.mode if not args.prompt else "custom",
            "description": result,
        }
        output_str = json.dumps(output, ensure_ascii=False, indent=2)
    else:
        output_str = result

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_str)
        print(f"Output written to {args.output}", file=sys.stderr)
    else:
        print(output_str)


if __name__ == "__main__":
    main()
