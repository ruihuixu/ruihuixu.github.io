# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Hugo static blog with fully custom dark tech theme (no theme submodule). Deployed to GitHub Pages via `.github/workflows/hugo.yaml`. Hugo version: `0.152.2` extended.

## Commands

```bash
hugo server -D          # local preview with drafts
hugo server             # local preview (published only)
hugo --minify           # production build
```

## Vision / Image Reading

When you need to visually understand an image (screenshot, diagram, chart, UI), use:

```bash
python3 scripts/read_image.py <path> [--mode ui|diagram|chart|code|text|photo|diff] [-p "custom prompt"] [--json]
```

See `.claude/skills/image-reader.md` for full usage guide. The main model has no vision; this tool bridges the gap via Qwen VL (DashScope). Key set to `DASHSCOPE_API_KEY` in `.claude/settings.local.json`.

No submodule setup needed — the theme is entirely custom.

## Architecture

- **`hugo.toml`** — site config (baseURL `https://rayx750.github.io/`, menus, taxonomies, `mainSections = ["notes", "misc", "projects"]`)
- **`layouts/_default/baseof.html`** — root template: loads `main.css`, conditionally loads `article.css` on single pages, loads `main.js`, renders `header.html` + main block + `footer.html`
- **`layouts/index.html`** — homepage assembles partials: `hero.html` → `projects.html` → `notes.html` → `misc.html`
- **`layouts/_default/single.html`** — article page template
- **`layouts/_default/list.html`** — default section list; section-specific overrides at `layouts/notes/code/list.html`, `layouts/notes/recommendation/list.html`, `layouts/notes/tools/list.html`, `layouts/misc/list.html`, `layouts/profile/list.html`, `layouts/projects/list.html`
- **`layouts/taxonomy/`** — `term.html` and `terms.html` for tag/category pages
- **`static/css/main.css`** — all base styles (1486 lines, custom dark tech theme)
- **`static/css/article.css`** — article-specific typography and content styling
- **`static/js/main.js`** — site-wide JS (nav, theme, interactions)
- **`data/profile.yaml`** — personal profile data (name, avatar, bio, skills, education, achievements)
- **`data/social.yaml`** — social links

## Content Structure

| Section | Path | Purpose |
|---------|------|---------|
| Code notes | `content/notes/code/` | Algorithm/LeetCode notes (Chinese filenames, English slugs) |
| RecSys notes | `content/notes/recommendation/` | Recommendation system paper notes |
| Tools notes | `content/notes/tools/` | Dev tool references |
| Misc | `content/misc/` | Reading notes, etc. |
| Projects | `content/projects/` | Project showcase |
| Profile | `content/profile/` | About me page |

All front matter uses YAML format (`---`). Key fields: `title`, `date`, `draft`, `slug`, `tags`, `categories`, `description`.

`content/notes/code/_index.md` uses `cascade.tags` to apply default tags to all pages in that section.

## Scoped Instructions

`.github/instructions/leetcode-writing-guide.md` applies to `content/notes/code/**/*.md` — defines file naming, front matter standards, article structure (A+B paradigm), code/diagram conventions, and quality checklist. Takes precedence over global instructions for files in that path.

## AI Workflows

- `.github/workflows/qwen-invoke.yml` — triggers AI content generation on issue comment
- `.github/workflows/qwen-triage.yml` — auto-triage issues with AI labels

## Do Not Edit

- `public/` — Hugo generated output
- `resources/_gen/` — Hugo resource cache
