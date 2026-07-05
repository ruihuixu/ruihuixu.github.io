#!/usr/bin/env python3
"""
微信读书数据同步脚本
拉取阅读统计数据 → 生成 data/weread.json（含阅读人格文本）
用法: python scripts/sync_weread.py
"""
import json, os, sys
from datetime import datetime
from urllib import request

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
        print("⚠️  skill 需要升级:", data["upgrade_info"]["message"])
        sys.exit(1)
    return data


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, "..", "data", "weread.json")

    # 1. 总体数据
    print("📡 拉取总体阅读数据...")
    overall = call("/readdata/detail", mode="overall")

    # 2. 逐年数据 (2024-2026)
    yearly = {}
    for year in [2024, 2025, 2026]:
        ts = int(datetime(year, 1, 15).timestamp())
        print(f"📡 拉取 {year} 年数据...")
        yearly[str(year)] = call("/readdata/detail", mode="annually", baseTime=ts)

    # 3. 书架数据
    print("📡 拉取书架数据...")
    shelf = call("/shelf/sync")

    # ── 汇总统计 ──
    total_time = overall.get("totalReadTime", 0)
    read_days = overall.get("readDays", 0)
    read_stat = {s["stat"]: s["counts"] for s in overall.get("readStat", [])}

    # ── 雷达图数据 ──
    radar = []
    for c in overall.get("preferCategory", []):
        radar.append({
            "category": c.get("categoryTitle", ""),
            "hours": round(c.get("readingTime", 0) / 3600, 1),
            "count": c.get("readingCount", 0),
        })

    # ── 时间线数据（分类×年份矩阵） ──
    # 收集所有出现过的分类
    all_cats = set()
    for ydata in yearly.values():
        for c in ydata.get("preferCategory", []):
            all_cats.add(c.get("categoryTitle", ""))
    all_cats = sorted(all_cats)

    years_sorted = sorted(yearly.keys())
    timeline = {"years": years_sorted, "categories": []}
    for cat in all_cats:
        hours_by_year = []
        for y in years_sorted:
            ydata = yearly[y]
            found = next((c for c in ydata.get("preferCategory", []) if c.get("categoryTitle") == cat), None)
            h = round(found.get("readingTime", 0) / 3600, 1) if found else 0
            hours_by_year.append(h)
        total_h = sum(hours_by_year)
        if total_h > 0.5:  # 过滤掉太小的
            timeline["categories"].append({
                "name": cat,
                "hours": hours_by_year,
                "total": round(total_h, 1),
            })

    # ── 投入最深 TOP10 ──
    longest = []
    for b in overall.get("readLongest", []):
        bk = b.get("book", {})
        longest.append({
            "title": bk.get("title", ""),
            "author": bk.get("author", ""),
            "cover": bk.get("cover", ""),
            "hours": round(b.get("readTime", 0) / 3600, 1),
            "tags": b.get("tags", []),
            "deepLink": bk.get("deepLink", ""),
        })

    # ── 书架统计 ──
    books = shelf.get("books", [])
    shelf_stats = {
        "total": len(books),
        "finished": sum(1 for b in books if b.get("finishReading") == 1),
        "reading": sum(1 for b in books if b.get("finishReading") != 1),
    }

    # ── 偏好分析 ──
    prefer_author = []
    for a in overall.get("preferAuthor", []):
        prefer_author.append({"name": a.get("name", ""), "count": a.get("count", 0), "readTime": a.get("readTime", "")})
    prefer_time_word = overall.get("preferTimeWord", "")

    # ── 自动生成阅读人格文本 ──
    personality = generate_personality(radar, read_stat, total_time, read_days, prefer_time_word, yearly)

    # ── 组装输出 ──
    output = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "stats": {
            "totalBooks": read_stat.get("读过", "?"),
            "finishedBooks": read_stat.get("读完", "?"),
            "totalHours": round(total_time / 3600, 1),
            "readDays": read_days,
            "notes": read_stat.get("笔记", "?"),
            "shelfBooks": shelf_stats["total"],
        },
        "radar": radar,
        "timeline": timeline,
        "longest": longest,
        "preferAuthor": prefer_author,
        "preferTimeWord": prefer_time_word,
        "personality": personality,
    }

    os.makedirs(os.path.dirname(data_path), exist_ok=True)
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"✅ 数据已写入 {data_path}")
    print(f"   读过 {read_stat.get('读过','?')} · 读完 {read_stat.get('读完','?')} · {round(total_time/3600,1)}h · {read_days}天")


def generate_personality(radar, read_stat, total_time, read_days, prefer_time_word, yearly):
    """基于数据自动生成阅读人格描述"""
    hours = round(total_time / 3600, 1)
    finished = read_stat.get("读完", "?")
    total_read = read_stat.get("读过", "?")

    # 找 top 3 分类
    top3 = sorted(radar, key=lambda x: x["hours"], reverse=True)[:3]

    # 分析趋势：比较2024和2026的分类变化
    y24 = yearly.get("2024", {}).get("preferCategory", [])
    y26 = yearly.get("2026", {}).get("preferCategory", [])
    cat_24 = {c["categoryTitle"]: c.get("readingTime", 0) for c in y24}
    cat_26 = {c["categoryTitle"]: c.get("readingTime", 0) for c in y26}

    # 找出增长最多的分类
    growth = {}
    for cat in set(list(cat_24.keys()) + list(cat_26.keys())):
        growth[cat] = cat_26.get(cat, 0) - cat_24.get(cat, 0)
    rising = sorted(growth.items(), key=lambda x: x[1], reverse=True)[:2]
    falling = sorted(growth.items(), key=lambda x: x[1])[:2]

    # 组装人格文本
    lines = []

    # 开篇：总体画像
    lines.append(f"从 2024 年至今，累计阅读 **{hours:.0f} 小时**，涉猎 **{total_read} 本书**，读完 **{finished} 本**。{prefer_time_word}。")

    # 核心兴趣
    top_names = "、".join([c["category"] for c in top3])
    lines.append(f"")
    lines.append(f"阅读光谱以 **{top_names}** 为三重核心。其中「{top3[0]['category']}」投入最深（{top3[0]['hours']}h），「{top3[1]['category']}」（{top3[1]['hours']}h）与「{top3[2]['category']}」（{top3[2]['hours']}h）紧随其后。")

    # 趋势
    if rising and rising[0][1] > 0:
        r_name, r_delta = rising[0]
        r_h = round(r_delta / 3600, 1)
        lines.append(f"")
        lines.append(f"阅读兴趣正经历一次明显的「向内转」：**{r_name}** 类异军突起（相比 2024 年增长 {r_h}h），从书架上的边缘类别变成了主力投入。")
    if falling and falling[0][1] < 0:
        f_name, f_delta = falling[0]
        f_h = round(abs(f_delta) / 3600, 1)
        if f_h > 1:
            lines.append(f"与此同时，「{f_name}」的投入有所回落（减少约 {f_h}h），兴趣焦点在收窄和深化。")

    # 阅读习惯
    lines.append(f"")
    if read_days >= 300:
        lines.append(f"**{read_days} 天**的阅读天数意味着几乎每天都有翻开书本——这不是突击式阅读，而是融入日常的持续习惯。")
    elif read_days >= 200:
        lines.append(f"**{read_days} 天**的阅读天数意味着大约两天中就有一天在阅读，阅读已经成为生活中的固定锚点。")

    # 深度 vs 广度
    if radar:
        max_h = max(c["hours"] for c in radar)
        min_h = min(c["hours"] for c in radar)
        if max_h / (min_h + 0.1) > 5:
            lines.append(f"阅读偏好非常集中——投入最多的类别是最少的 {max_h/(min_h+0.1):.0f} 倍，你的阅读不是「什么都看一点」，而是「把感兴趣的读到透」。")
        else:
            lines.append(f"八个类别之间分布比较均衡，广度与深度兼而有之。")

    # 结尾
    lines.append(f"")
    lines.append(f"整体来看，这是一位**思考型读者**的阅读轨迹：偏好能提供认知框架的严肃读物（社科、心理、历史、哲学），而非消遣型内容。阅读是为了理解世界如何运转，以及人在其中如何自处。")

    return "\n".join(lines)


if __name__ == "__main__":
    main()
