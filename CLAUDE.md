# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Hugo static blog deployed to GitHub Pages, using the Ananke theme as a git submodule.

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
| `content/` | Markdown content (leetcode, tools, projects, interview) |
| `data/profile.yaml` | Sidebar profile config (name, avatar, bio, skills) |
| `hugo.toml` | Site config, menus, params |
| `layouts/` | Custom templates (if any) |
| `static/` | Static assets (images, CSS) |
| `themes/ananke/` | Theme submodule (do not modify directly) |

## Content Conventions

- **Section index**: `content/{section}/_index.md`
- **Articles**: `content/{section}/{article}.md`
- **Front matter**: YAML format (`--- ... ---`)
- **Tags**: Use YAML list format
- **LeetCode section**: Uses `cascade.tags` for default "Algorithm" tag

## Theme Overrides

Use Hugo lookup order to override theme files without modifying the submodule:

| Purpose | Override Path |
|---------|---------------|
| Homepage | `layouts/index.html` |
| Header | `layouts/partials/site-header.html` |
| Custom CSS | `static/css/custom.css` (loaded via `params.custom_css`) |

## Do Not Modify

| Path | Reason |
|------|--------|
| `public/` | Generated output |
| `resources/_gen/` | Hugo resource cache |
| `themes/ananke/` | Git submodule |

## Instructions

- `.github/copilot-instructions.md`: Persona and workflow guidelines
- `.github/instructions/leetcode-writing-guide.md`: LeetCode article writing standard (applies to `content/leetcode/**/*.md`)
