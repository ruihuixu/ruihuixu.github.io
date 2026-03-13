# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Hugo static blog deployed to GitHub Pages with custom dark tech theme.

## Commands

```bash
# Local preview (with drafts)
hugo server -D

# Local preview (without drafts)
hugo server

# Production build
hugo --minify

# Initialize theme submodule (if missing)
git submodule update --init --recursive
```

## Architecture

- **Hugo** SSG with `hugo.toml` config
- **Theme**: Ananke (git submodule at `themes/ananke`)
- **Deployment**: GitHub Actions (`.github/workflows/hugo.yaml`) → GitHub Pages
- **Base URL**: `https://rayx750.github.io/`

## Directory Structure

| Path | Purpose |
|------|---------|
| `content/` | Markdown content (notes/code, notes/tools, notes/recommendation, projects, misc) |
| `data/profile.yaml` | Profile config (name, avatar, bio, info, skills, education, achievements) |
| `hugo.toml` | Site config, menus, params |
| `layouts/` | Custom templates (index, partials, list, single) |
| `static/` | Static assets (images, CSS, JS) |
| `themes/ananke/` | Theme submodule (do not modify directly) |

## Content Conventions

- **Section index**: `content/{section}/_index.md`
- **Articles**: `content/{section}/{article}.md`
- **Front matter**: YAML format (`--- ... ---`)
- **Tags**: Use YAML list format
- **Notes section**: `content/notes/code/_index.md` uses `cascade.tags` for default "Algorithm" tag

## Theme Overrides

Custom dark tech theme implemented in:

| Purpose | File |
|---------|------|
| Homepage | `layouts/index.html` |
| Header | `layouts/partials/header.html` |
| Main CSS | `static/css/main.css` |
| Article CSS | `static/css/article.css` |

## Do Not Modify

| Path | Reason |
|------|--------|
| `public/` | Generated output |
| `resources/_gen/` | Hugo resource cache |
| `themes/ananke/` | Git submodule |

## Instructions

- `.github/copilot-instructions.md`: Persona and workflow guidelines
- `.github/instructions/leetcode-writing-guide.md`: LeetCode article writing standard (applies to `content/notes/code/**/*.md`)
