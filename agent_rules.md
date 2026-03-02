# Factory 471 Website - AI Agent Rules

This document outlines the rules and architecture guidelines for AI agents working on this repository.

## 1. Project Architecture (CRITICAL)
- This is a static website that hosts documentation (Privacy Policies, Terms of Service, Support) for Factory 471 apps (Snow Record, SSAK Photo Cleaner, Wayin Korea, ChemViz).
- **NEVER** manually edit the generated HTML document pages (e.g., `*-privacy.html`, `*-terms.html`, `*-support.html`, `about.html`). Any manual changes to these files will be overwritten upon the next build.
- The HTML pages are generated from Markdown files using a custom Python script.

## 2. Content Update Workflow
- The source of truth for documents are Markdown files located in the `notion_exports/` directory or app-specific directories like `ChemViz/`.
- **To update existing documents:** Edit the respective `.md` file and run `python build_site_pages.py` to regenerate the HTML.
- **To import new Notion exports:** 
  1. Place the exported `.zip` files from Notion into the root directory.
  2. Run `python extract_zips.py` to extract them into `notion_exports/`.
  3. Run `python build_site_pages.py` to build the HTML.

## 3. Adding New Apps or Documents
- Document configurations and app mappings are hardcoded in `build_site_pages.py`.
- If you need to add a new app or a new document type, you MUST update the `DOCS` and `APPS` dictionaries at the top of `build_site_pages.py`.
- Ensure the `md_glob` correctly matches the Markdown filenames.

## 4. Styling and Frontend Design
- The site uses **Tailwind CSS via CDN**. There is no Node.js build step, `package.json`, or `tailwind.config.js` file.
- Tailwind configuration (colors, fonts) is embedded directly as a string (`TAILWIND_CONFIG`) inside `build_site_pages.py`. If you need to change theme colors or fonts, modify that Python string.
- The UI uses Material Symbols Outlined for icons.
- Pages support Dark Mode (using the `class` strategy on the `<html>` tag) and multi-language tabs (handled by `LANG_SCRIPT` in the python generator).

## 5. Deployment
- Deployment is automated via GitHub Actions (`.github/workflows/deploy.yml`).
- Pushing to the `main` branch triggers a workflow that runs `python build_site_pages.py` and deploys the generated site to GitHub Pages.

## 6. Development Rules
- The project uses Python 3 for build logic and HTML/Vanilla JS with Tailwind (CDN) for the frontend.
- Markdown processing and HTML rendering logic (including language detection for Ko/En/Ja/Common) is custom-built inside `build_site_pages.py`. Do not introduce external Markdown parsing libraries (like `markdown` or `mistune`) unless explicitly asked, as the custom parser handles specific Notion formatting requirements.
- Always verify changes by running `python build_site_pages.py` locally and checking the generated HTML before committing.
