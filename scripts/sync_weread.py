#!/usr/bin/env python3
"""
微信读书全量数据同步脚本
拉取：书架、阅读统计、分类偏好、逐年数据、笔记、书籍详情
输出：
  1. data/weread.json       — 博客用（精简版）
  2. Obsidian vault 笔记     — 个人知识库用（全量版）
     /阅读/阅读概览.md
     /阅读/书架全览.md
     /阅读/已读清单.md
     /阅读/阅读轨迹.md
用法: python scripts/sync_weread.py [--blog-only|--obsidian-only]
"""
import json, os, sys, argparse
from datetime import datetime
from urllib import request
from collections import Counter

API = "https://i.weread.qq.com/api/agent/gateway"
HEADERS = {
    "Authorization": f"Bearer {os.environ.get('WEREAD_API_KEY', '')}",
    "Content-Type": "application/json",
}

def call(api_name, **params):
    body = {"api_name": api_name, "skill_version": "1.0.4", **params}
    req = request.Request(API, data=json.dumps(body).encode(), headers=HEADERS, method="POST")
    with request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    if "upgrade_info" in data:
        raise SystemExit("Skill 需要升级: " + data["upgrade_info"]["message"])
    return data


def fmt_time(ts):
    """Unix 时间戳 → YYYY-MM-DD"""
    if not ts:
        return ""
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d")

def fmt_duration(sec):
    """秒 → X小时Y分钟"""
    h, m = divmod(int(sec), 3600)
    m //= 60
    return f"{h}小时{m}分钟" if h > 0 else f"{m}分钟"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--blog-only", action="store_true")
    parser.add_argument("--obsidian-only", action="store_true")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    blog_data_path = os.path.join(script_dir, "..", "data", "weread.json")
    vault_path = "/mnt/e/MyNotes"

    # ═══ 1. 拉取所有数据 ═══
    print("📡 拉取书架...")
    shelf = call("/shelf/sync")

    print("📡 拉取总体阅读统计...")
    overall = call("/readdata/detail", mode="overall")

    print("📡 拉取逐年数据 (2024-2026)...")
    yearly = {}
    for year in [2024, 2025, 2026]:
        ts = int(datetime(year, 1, 15).timestamp())
        yearly[str(year)] = call("/readdata/detail", mode="annually", baseTime=ts)

    print("📡 拉取笔记列表...")
    notebooks = call("/user/notebooks", count=200)
    note_books = notebooks.get("books", [])
    # 建立 bookId → 笔记数映射
    note_count_map = {}
    for nb in note_books:
        bk = nb.get("book", {})
        bid = bk.get("bookId", "")
        note_count_map[bid] = nb.get("noteCount", 0)

    # ═══ 2. 处理书架数据 ═══
    books = shelf.get("books", [])
    albums = shelf.get("albums", [])
    archive = shelf.get("archive", [])

    # 分类统计
    cat_counter = Counter(b.get("category", "未分类") for b in books)

    # 书架条目列表
    shelf_items = []
    for b in books:
        shelf_items.append({
            "title": b.get("title", ""),
            "author": b.get("author", ""),
            "category": b.get("category", "未分类"),
            "finished": b.get("finishReading", 0) == 1,
            "secret": b.get("secret", 0) == 1,
            "lastRead": fmt_time(b.get("readUpdateTime")),
            "cover": b.get("cover", ""),
            "notes": note_count_map.get(b.get("bookId", ""), 0),
        })

    # 书单详情
    booklist_details = []
    book_id_map = {b["bookId"]: b for b in books}
    for a in archive:
        ids = a.get("bookIds", [])
        titles = []
        for bid in ids:
            bk = book_id_map.get(bid, {})
            titles.append(bk.get("title", bid))
        booklist_details.append({
            "name": a.get("name", ""),
            "count": len(ids),
            "books": titles,
        })

    # ═══ 3. 处理阅读统计数据 ═══
    read_stat = {s["stat"]: s["counts"] for s in overall.get("readStat", [])}
    total_time = overall.get("totalReadTime", 0)
    read_days = overall.get("readDays", 0)

    # 偏好分类
    prefer_cats = []
    for c in overall.get("preferCategory", []):
        prefer_cats.append({
            "category": c.get("categoryTitle", ""),
            "parent": c.get("parentCategoryTitle", ""),
            "hours": round(c.get("readingTime", 0) / 3600, 1),
            "count": c.get("readingCount", 0),
        })

    # 读得最多
    longest = []
    for b in overall.get("readLongest", []):
        bk = b.get("book", {})
        bid = bk.get("bookId", "")
        longest.append({
            "title": bk.get("title", ""),
            "author": bk.get("author", ""),
            "hours": round(b.get("readTime", 0) / 3600, 1),
            "tags": b.get("tags", []),
            "cover": bk.get("cover", ""),
            "notes": note_count_map.get(bid, 0),
        })

    # 偏好作者
    prefer_authors = []
    for a in overall.get("preferAuthor", []):
        prefer_authors.append({
            "name": a.get("name", ""),
            "count": a.get("count", 0),
            "readTime": a.get("readTime", ""),
        })

    # ═══ 4. 逐年趋势 ═══
    all_cats = set()
    for ydata in yearly.values():
        for c in ydata.get("preferCategory", []):
            all_cats.add(c.get("categoryTitle", ""))
    all_cats = sorted(all_cats)

    years_sorted = sorted(yearly.keys())
    timeline_data = {"years": years_sorted, "categories": []}
    for cat in all_cats:
        hours_by_year = []
        for y in years_sorted:
            ydata = yearly[y]
            found = next((c for c in ydata.get("preferCategory", []) if c.get("categoryTitle") == cat), None)
            h = round(found.get("readingTime", 0) / 3600, 1) if found else 0
            hours_by_year.append(h)
        total_h = sum(hours_by_year)
        if total_h > 0.5:
            timeline_data["categories"].append({
                "name": cat,
                "hours": hours_by_year,
                "total": round(total_h, 1),
            })

    # ═══ 5. 阅读人格 ═══
    personality = generate_personality(prefer_cats, read_stat, total_time, read_days, overall, yearly)

    # ═══ 6. 输出博客 JSON ═══
    if not args.obsidian_only:
        blog_json = {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "stats": {
                "totalBooks": read_stat.get("读过", "?"),
                "finishedBooks": read_stat.get("读完", "?"),
                "totalHours": round(total_time / 3600, 1),
                "readDays": read_days,
                "notes": read_stat.get("笔记", "?"),
                "shelfBooks": len(books),
            },
            "radar": prefer_cats,
            "timeline": timeline_data,
            "longest": longest,
            "preferAuthor": prefer_authors,
            "preferTimeWord": overall.get("preferTimeWord", ""),
            "personality": personality,
        }
        os.makedirs(os.path.dirname(blog_data_path), exist_ok=True)
        with open(blog_data_path, "w", encoding="utf-8") as f:
            json.dump(blog_json, f, ensure_ascii=False, indent=2)
        print(f"✅ 博客数据 → {blog_data_path}")

    # ═══ 7. 生成 Obsidian 笔记 ═══
    if not args.blog_only:
        vault_reading = os.path.join(vault_path, "阅读")
        os.makedirs(vault_reading, exist_ok=True)

        # 7.1 阅读概览
        generate_overview(vault_reading, read_stat, total_time, read_days, prefer_cats, personality, overall)

        # 7.2 书架全览
        generate_shelf(vault_reading, shelf_items, cat_counter, booklist_details, len(albums), shelf.get("mp"))

        # 7.3 已读清单
        generate_read_list(vault_reading, longest, prefer_cats, prefer_authors)

        # 7.4 阅读轨迹
        generate_timeline(vault_reading, timeline_data, yearly, note_count_map)

        print(f"✅ Obsidian 笔记 → {vault_reading}/")

    print("🎉 同步完成！")
    print(f"   读过 {read_stat.get('读过','?')} · 读完 {read_stat.get('读完','?')} · {round(total_time/3600,1)}h · {read_days}天")


def generate_overview(path, read_stat, total_time, read_days, prefer_cats, personality, overall):
    hours = round(total_time / 3600, 1)
    finished = read_stat.get("读完", "?")
    total = read_stat.get("读过", "?")
    notes = read_stat.get("笔记", "?")

    # 偏好分类表格
    cat_rows = ""
    for c in prefer_cats[:8]:
        bar = "█" * int(c["hours"] / 2) + "░" * (15 - int(c["hours"] / 2))
        cat_rows += f"| {c['category']} | {c['hours']}h | {c['count']}本 | `{bar}` |\n"

    content = f"""---
tags: [阅读, 微信读书]
created: {datetime.now().strftime('%Y-%m-%d')}
---

# 📊 阅读概览

> 数据更新于 {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 核心数字

| 指标 | 数值 |
|------|------|
| 读过 | **{total}** |
| 读完 | **{finished}** |
| 累计时长 | **{hours} 小时** |
| 阅读天数 | **{read_days} 天** |
| 笔记 | **{notes}** |
| 偏好时段 | {overall.get('preferTimeWord', '-')} |

## 阅读光谱（分类偏好）

| 分类 | 时长 | 本数 | 投入度 |
|------|------|------|--------|
{cat_rows}

## 阅读人格

{personality}

## 相关笔记

- [[书架全览]] — 全部 54 本书籍
- [[已读清单]] — 投入最深的 10 本书
- [[阅读轨迹]] — 逐年阅读趋势
"""
    with open(os.path.join(path, "阅读概览.md"), "w", encoding="utf-8") as f:
        f.write(content)


def generate_shelf(path, items, cat_counter, booklists, album_count, mp):
    # 分类统计
    cat_stats = ""
    for cat, n in cat_counter.most_common():
        cat_stats += f"- **{cat}**：{n} 本\n"

    # 书架列表（按分类分组）
    by_cat = {}
    for item in items:
        c = item["category"]
        by_cat.setdefault(c, []).append(item)

    shelf_list = ""
    for cat in sorted(by_cat.keys()):
        shelf_list += f"\n### {cat}\n\n"
        shelf_list += "| 书名 | 作者 | 状态 | 笔记 | 最近阅读 |\n"
        shelf_list += "|------|------|------|------|----------|\n"
        for item in sorted(by_cat[cat], key=lambda x: x["lastRead"] or "", reverse=True):
            status = "✅ 读完" if item["finished"] else "📖 在读"
            lock = "🔒" if item["secret"] else ""
            notes = f"{item['notes']}条" if item["notes"] else "-"
            shelf_list += f"| {lock}{item['title']} | {item['author']} | {status} | {notes} | {item['lastRead']} |\n"

    # 书单
    bl_section = ""
    if booklists:
        bl_section = "\n## 书单\n\n"
        for bl in booklists:
            bl_section += f"### 📚 {bl['name']}（{bl['count']} 本）\n\n"
            for t in bl["books"][:10]:
                bl_section += f"- {t}\n"
            if len(bl["books"]) > 10:
                bl_section += f"- *...等 {len(bl['books'])} 本*\n"
            bl_section += "\n"

    content = f"""---
tags: [阅读, 书架, 微信读书]
created: {datetime.now().strftime('%Y-%m-%d')}
---

# 📚 书架全览

> 共 {len(items)} 本电子书{' + ' + str(album_count) + ' 有声书' if album_count else ''}{' + 文章收藏' if mp else ''}

## 分类分布

{cat_stats}
{bl_section}
## 完整书架

{shelf_list}
"""
    with open(os.path.join(path, "书架全览.md"), "w", encoding="utf-8") as f:
        f.write(content)


def generate_read_list(path, longest, prefer_cats, prefer_authors):
    # TOP10 书籍
    book_rows = ""
    for i, b in enumerate(longest):
        tags = ", ".join(b["tags"]) if b["tags"] else "-"
        notes = f"{b['notes']}条" if b["notes"] else "-"
        book_rows += f"| {i+1} | {b['title']} | {b['author']} | {b['hours']}h | {notes} | {tags} |\n"

    # 偏好作者
    author_rows = ""
    for a in prefer_authors:
        author_rows += f"| {a['name']} | {a['count']}本 | {a['readTime']} |\n"

    content = f"""---
tags: [阅读, 已读, 微信读书]
created: {datetime.now().strftime('%Y-%m-%d')}
---

# 📖 已读清单

## 投入最深 TOP 10

| # | 书名 | 作者 | 阅读时长 | 笔记 | 标签 |
|---|------|------|----------|------|------|
{book_rows}

## 偏好作者

| 作者 | 阅读本数 | 阅读时长 |
|------|----------|----------|
{author_rows}

## 关联

- [[阅读概览]] — 阅读统计与人格分析
- [[阅读轨迹]] — 逐年阅读趋势
- [[书架全览]] — 全部书架
"""
    with open(os.path.join(path, "已读清单.md"), "w", encoding="utf-8") as f:
        f.write(content)


def generate_timeline(path, timeline_data, yearly, note_count_map):
    # 逐年总览
    year_overview = ""
    for y, ydata in yearly.items():
        total = ydata.get("totalReadTime", 0)
        days = ydata.get("readDays", 0)
        cats = ydata.get("preferCategory", [])
        top_cat = cats[0]["categoryTitle"] if cats else "-"
        year_overview += f"| {y} | {fmt_duration(total)} | {days}天 | {top_cat} |\n"

    # 分类趋势矩阵
    matrix = "| 分类 | " + " | ".join(timeline_data["years"]) + " | 总计 |\n"
    matrix += "|------|" + "|".join(["------"] * (len(timeline_data["years"]) + 1)) + "|\n"
    for cat in sorted(timeline_data["categories"], key=lambda x: x["total"], reverse=True):
        hours_str = " | ".join(f"{h}h" if h > 0 else "-" for h in cat["hours"])
        matrix += f"| {cat['name']} | {hours_str} | {cat['total']}h |\n"

    # 逐年 details
    year_details = ""
    for y, ydata in yearly.items():
        total = ydata.get("totalReadTime", 0)
        days = ydata.get("readDays", 0)
        cats = ydata.get("preferCategory", [])

        year_details += f"\n### {y} 年 — {fmt_duration(total)} / {days}天\n\n"
        year_details += "| 分类 | 时长 | 本数 |\n|------|------|------|\n"
        for c in cats:
            h = round(c.get("readingTime", 0) / 3600, 1)
            n = c.get("readingCount", 0)
            year_details += f"| {c.get('categoryTitle', '')} | {h}h | {n}本 |\n"

        # 读得最多的书
        rl = ydata.get("readLongest", [])
        if rl:
            year_details += f"\n**读得最多：**\n"
            for b in rl[:5]:
                bk = b.get("book", {})
                h = round(b.get("readTime", 0) / 3600, 1)
                year_details += f"- {bk.get('title', '')} — {h}h\n"

    content = f"""---
tags: [阅读, 统计, 微信读书]
created: {datetime.now().strftime('%Y-%m-%d')}
---

# 📈 阅读轨迹

## 逐年总览

| 年份 | 阅读时长 | 阅读天数 | 最偏好分类 |
|------|----------|----------|------------|
{year_overview}

## 分类 × 年份矩阵

{matrix}
{year_details}

## 关联

- [[阅读概览]] — 总体统计与人格
- [[已读清单]] — TOP 书籍
- [[书架全览]] — 全部书架
"""
    with open(os.path.join(path, "阅读轨迹.md"), "w", encoding="utf-8") as f:
        f.write(content)


def generate_personality(prefer_cats, read_stat, total_time, read_days, overall, yearly):
    hours = round(total_time / 3600, 1)
    finished = read_stat.get("读完", "?")
    total_read = read_stat.get("读过", "?")
    prefer_time = overall.get("preferTimeWord", "")

    top3 = sorted(prefer_cats, key=lambda x: x["hours"], reverse=True)[:3]

    y24 = yearly.get("2024", {}).get("preferCategory", [])
    y26 = yearly.get("2026", {}).get("preferCategory", [])
    cat_24 = {c["categoryTitle"]: c.get("readingTime", 0) for c in y24}
    cat_26 = {c["categoryTitle"]: c.get("readingTime", 0) for c in y26}

    growth = {}
    for cat in set(list(cat_24.keys()) + list(cat_26.keys())):
        growth[cat] = cat_26.get(cat, 0) - cat_24.get(cat, 0)
    rising = sorted(growth.items(), key=lambda x: x[1], reverse=True)[:2]
    falling = sorted(growth.items(), key=lambda x: x[1])[:2]

    lines = []
    top_names = "、".join([c["category"] for c in top3])
    lines.append(f"从 2024 年至今，累计阅读 **{hours:.0f} 小时**，涉猎 **{total_read}**，读完 **{finished}**。{prefer_time}。")
    lines.append("")
    lines.append(f"阅读光谱以 **{top_names}** 为三重核心。其中「{top3[0]['category']}」投入最深（{top3[0]['hours']}h），「{top3[1]['category']}」（{top3[1]['hours']}h）与「{top3[2]['category']}」（{top3[2]['hours']}h）紧随其后。")

    if rising and rising[0][1] > 0:
        r_name, r_delta = rising[0]
        r_h = round(r_delta / 3600, 1)
        lines.append("")
        lines.append(f"阅读兴趣正经历一次明显的「向内转」：**{r_name}** 类异军突起（相比 2024 年增长 {r_h}h），从书架上的边缘类别变成了主力投入。")

    if falling and falling[0][1] < 0:
        f_name, f_delta = falling[0]
        f_h = round(abs(f_delta) / 3600, 1)
        if f_h > 1:
            lines.append(f"与此同时，「{f_name}」的投入有所回落（减少约 {f_h}h），兴趣焦点在收窄和深化。")

    lines.append("")
    lines.append(f"**{read_days} 天**的阅读天数意味着几乎每天都有翻开书本——这不是突击式阅读，而是融入日常的持续习惯。")
    lines.append("")
    lines.append("整体来看，这是一位**思考型读者**的阅读轨迹：偏好能提供认知框架的严肃读物（社科、心理、历史、哲学），而非消遣型内容。阅读是为了理解世界如何运转，以及人在其中如何自处。")

    return "\n".join(lines)


if __name__ == "__main__":
    main()
