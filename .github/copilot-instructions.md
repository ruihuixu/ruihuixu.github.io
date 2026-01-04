# Copilot instructions for this repo (Hugo blog)

## Project big picture
- This is a **Hugo** static site. Site config is in `hugo.toml`.
- Theme is **Ananke** as a **git submodule** at `themes/ananke` (see `.gitmodules`). Prefer overriding theme templates via Hugo lookup order rather than editing the submodule.
- Deployment to GitHub Pages is done by GitHub Actions in `.github/workflows/hugo.yaml` using `hugo --minify` and publishing the generated `public/` artifact.

## Local workflows (Windows-friendly)
- Preview locally: `hugo server` (add `-D` to include drafts).
- Production build: `hugo --minify`.
- If the theme isn’t present after checkout: `git submodule update --init --recursive`.

## Repo conventions and “don’t edit” directories
- **Do not hand-edit generated output** in `public/` or `resources/_gen/`. Regenerate via Hugo instead.
- Site content lives under `content/`:
  - Section list pages use `_index.md` (e.g. `content/leetcode/_index.md`, `content/tools/_index.md`).
  - Individual articles are section markdown files (e.g. `content/leetcode/704-binary-search.md`).
- This repo’s existing content primarily uses **YAML front matter** (`--- ... ---`). (Note: `archetypes/default.md` uses TOML `+++`; follow the existing content style when editing/adding posts.)

## Theme overrides used by this site
- Homepage is customized in `layouts/index.html` and reads sidebar data from `data/profile.yaml` (avatar path points into `static/images/`).
- Header/nav is overridden in `layouts/partials/site-header.html` and renders items from `.Site.Menus.main` configured in `hugo.toml`.
- Styling tweaks are in `static/css/custom.css` and loaded via `params.custom_css` in `hugo.toml`.
- The templates use **Hugo Go templates** + Ananke/Tachyons-style classes; keep changes minimal and consistent with existing markup.

## Content patterns to preserve
- `content/leetcode/_index.md` uses `cascade.tags` to apply default tags to pages in that section; keep this behavior when reorganizing/adding pages.
- Keep taxonomy fields consistent with existing posts: `tags`, `categories`, `description`, `draft`, and `date`.

## When changing the homepage feed
- `layouts/index.html` paginates by `.Site.Params.mainSections`; if adjusting which sections appear in “Latest Activities”, update either `params.mainSections` in `hugo.toml` or the template logic accordingly.
