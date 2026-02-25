"""
build_site_pages.py — Markdown-based site builder for Factory 471
Reads .md files exported from Notion and builds HTML document pages.

Usage:
  python build_site_pages.py

Markdown files should be placed in ./notion_exports/
"""

import html as html_lib
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPORTS_DIR = ROOT / "notion_exports"

# ── Document config ──────────────────────────────────────────────────────────

DOCS = {
    "snow-support": {
        "title": "Snow Record - User Support",
        "md_glob": "Snow Record - User Support*.md",
        "out": "snow-record-support.html",
        "app": "snow",
        "label": "User Support",
        "kind": "support",
        "notion_url": "https://actually-hamster-aa2.notion.site/Snow-Record-User-Support-2fb5e95d9ec18059b7eeca6bb6e8edc0",
    },
    "snow-privacy": {
        "title": "Snow Record - Privacy Policy",
        "md_glob": "Snow Record - Privacy Policy*.md",
        "out": "snow-record-privacy.html",
        "app": "snow",
        "label": "Privacy Policy",
        "kind": "privacy",
        "notion_url": "https://actually-hamster-aa2.notion.site/Snow-Record-Privacy-Policy-2f95e95d9ec180a795c2e7620227c213",
    },
    "snow-terms": {
        "title": "Snow Record - Terms of Service",
        "md_glob": "Snow Record - Terms of Service*.md",
        "out": "snow-record-terms.html",
        "app": "snow",
        "label": "Terms of Service",
        "kind": "terms",
        "notion_url": "https://actually-hamster-aa2.notion.site/Snow-Record-Terms-of-Service-2f95e95d9ec180c4848adb22faecef63",
    },
    "ssak-support": {
        "title": "SSAK: Photo Cleaner - User Support",
        "md_glob": "SSAK Photo Cleaner - User Support*.md",
        "out": "ssak-photo-cleaner-support.html",
        "app": "ssak",
        "label": "User Support",
        "kind": "support",
        "notion_url": "https://actually-hamster-aa2.notion.site/SSAK-Photo-Cleaner-User-Support-3085e95d9ec18097a411c690806706a4",
    },
    "ssak-privacy": {
        "title": "SSAK: Photo Cleaner - Privacy Policy",
        "md_glob": "SSAK Photo Cleaner - Privacy Policy*.md",
        "out": "ssak-photo-cleaner-privacy.html",
        "app": "ssak",
        "label": "Privacy Policy",
        "kind": "privacy",
        "notion_url": "https://actually-hamster-aa2.notion.site/SSAK-Photo-Cleaner-Privacy-Policy-3085e95d9ec180958805c5f9b73f507e",
    },
    "ssak-terms": {
        "title": "SSAK: Photo Cleaner - Terms of Use",
        "md_glob": "SSAK Photo Cleaner - Terms of Use*.md",
        "out": "ssak-photo-cleaner-terms.html",
        "app": "ssak",
        "label": "Terms of Use",
        "kind": "terms",
        "notion_url": "https://actually-hamster-aa2.notion.site/SSAK-Photo-Cleaner-Terms-of-Use-3085e95d9ec180be81c7ed77c15ad967",
    },
    "wayin-privacy": {
        "title": "Wayin Korea - Privacy Policy",
        "md_glob": "Wayin Korea - Privacy Policy*.md",
        "out": "wayin-korea-privacy.html",
        "app": "wayin",
        "label": "Privacy Policy",
        "kind": "privacy",
        "notion_url": "https://actually-hamster-aa2.notion.site/Wayin-Korea-Privacy-Policy-30f5e95d9ec18022ae32db27838d3b8c",
    },
    "wayin-terms": {
        "title": "Wayin Korea - Terms of Service",
        "md_glob": "Wayin Korea - Terms of Service*.md",
        "out": "wayin-korea-terms.html",
        "app": "wayin",
        "label": "Terms of Service",
        "kind": "terms",
        "notion_url": "https://actually-hamster-aa2.notion.site/Wayin-Korea-Terms-of-Service-30f5e95d9ec180808495f51eb35965e6",
    },
    "factory-about": {
        "title": "Factory 471",
        "md_glob": "Factory 471*.md",
        "md_root": True,          # file lives in ROOT, not EXPORTS_DIR
        "out": "about.html",
        "app": None,
        "label": "About Us",
        "kind": "about",
        "notion_url": "https://actually-hamster-aa2.notion.site/Factory-471-30d5e95d9ec1806bade9cfeba9239800",
    },
}

APPS = {
    "snow": {
        "name": "Snow Record",
        "hub": "snow-record.html",
        "docs": ["snow-support", "snow-privacy", "snow-terms"],
    },
    "ssak": {
        "name": "SSAK: Photo Cleaner",
        "hub": "ssak-photo-cleaner.html",
        "docs": ["ssak-support", "ssak-privacy", "ssak-terms"],
    },
    "wayin": {
        "name": "Wayin Korea",
        "hub": "wayin-korea.html",
        "docs": ["wayin-privacy", "wayin-terms"],
    },
}

# ── Language detection ────────────────────────────────────────────────────────

RE_HANGUL = re.compile(r"[\uac00-\ud7a3]")
RE_KANA = re.compile(r"[\u3040-\u30ff]")
RE_CJK = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf]")
RE_LATIN = re.compile(r"[A-Za-z]")


def detect_lang(text: str, current_lang: str = "en") -> str:
    """Detect language of a text block.
    
    Uses character frequency analysis:
    - Hangul (Korean): 한글 characters → ko
    - Kana (Japanese): hiragana/katakana → ja  
    - CJK Kanji with no Hangul → ja (Japanese uses kanji too)
    - Latin characters dominant → en
    - Otherwise: inherit current_lang context (avoid 'common' bleeding)
    """
    hangul = len(RE_HANGUL.findall(text))
    kana = len(RE_KANA.findall(text))
    cjk = len(RE_CJK.findall(text))
    latin = len(RE_LATIN.findall(text))
    
    if hangul >= 3:
        return "ko"
    # Hangul + some CJK → still Korean
    if hangul >= 1 and cjk >= 1:
        return "ko"
    # Kana present → Japanese
    if kana >= 1:
        return "ja"
    # CJK kanji without Hangul → Japanese (Chinese is unlikely in these docs)
    if cjk >= 2 and hangul == 0:
        return "ja"
    # Clear Latin dominance → English
    if latin >= 5 and hangul == 0 and kana == 0 and cjk == 0:
        return "en"
    # Ambiguous (short text, numbers, punctuation, emoji only):
    # inherit section context instead of returning 'common'
    if current_lang in ("ko", "ja"):
        return current_lang
    return "en"


# ── Markdown → HTML renderer ─────────────────────────────────────────────────

URL_RE = re.compile(r"https?://[^\s\]\)\"'<>]+")


def esc(s: str) -> str:
    return escape(s, quote=True)


def render_inline(text: str) -> str:
    """Convert inline markdown (bold, italic, code, links) to HTML."""
    # Escape HTML first, then restore markdown markers temporarily
    # We work token-by-token to avoid double-escaping

    # Process in order: inline code, links, bold+italic, bold, italic, plain URLs
    result = []
    i = 0
    s = text

    # Use a regex-based approach
    INLINE_RE = re.compile(
        r"(`+)(.+?)\1"                                     # inline code
        r"|(\*\*\*|___)(.*?)\3"                            # bold+italic
        r"|(\*\*|__)(.+?)\5"                               # bold
        r"|(\*|_)(.+?)\7"                                  # italic
        r"|\[([^\]]*)\]\(([^)]*)\)"                        # link [text](url)
        r"|(https?://[^\s\]\)\"'<>]+)",                    # bare URL
        re.DOTALL,
    )

    last = 0
    for m in INLINE_RE.finditer(s):
        # Append escaped text before match
        result.append(esc(s[last:m.start()]))
        last = m.end()

        if m.group(1):  # inline code
            result.append(f"<code>{esc(m.group(2))}</code>")
        elif m.group(3):  # bold+italic
            result.append(f"<strong><em>{esc(m.group(4))}</em></strong>")
        elif m.group(5):  # bold
            result.append(f"<strong>{esc(m.group(6))}</strong>")
        elif m.group(7):  # italic
            result.append(f"<em>{esc(m.group(8))}</em>")
        elif m.group(9) is not None:  # markdown link
            link_text = m.group(9)
            link_url = m.group(10)
            # Skip internal notion anchor links (same-page)
            if link_url.startswith("#") or "notion.so" in link_url:
                result.append(esc(link_text) if link_text else "")
            else:
                result.append(
                    f'<a href="{esc(link_url)}" target="_blank" rel="noopener noreferrer">{esc(link_text)}</a>'
                )
        elif m.group(11):  # bare URL
            url = m.group(11)
            result.append(
                f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(url)}</a>'
            )

    result.append(esc(s[last:]))
    return "".join(result)


def md_to_html_blocks(md_text: str) -> list[dict]:
    """
    Parse markdown into a list of block dicts:
      { "type": "h1"/"h2"/"h3"/"h4"/"p"/"ul"/"ol"/"hr"/"blockquote"/"pre",
        "html": "<tag>...</tag>",
        "lang": "en"/"ko"/"ja"/"common",
        "raw_text": "plain text" }
    """
    lines = md_text.splitlines()
    blocks = []
    i = 0
    current_lang = "en"

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # ── Horizontal rule ──────────────────────────────────────────────────
        if re.match(r"^[-*_]{3,}$", stripped):
            blocks.append({"type": "hr", "html": "<hr/>", "raw_text": "", "lang": "common"})
            i += 1
            continue

        # ── Headings ─────────────────────────────────────────────────────────
        m = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if m:
            level = len(m.group(1))
            content = m.group(2).strip()
            inner = render_inline(content)
            tag = f"h{min(level, 4)}"
            # raw_text: strip HTML tags, then unescape entities so TOC shows & not &amp;
            raw = html_lib.unescape(re.sub(r"<[^>]+>", "", inner))
            lang = detect_lang(raw, current_lang)
            if lang in ("ko", "ja", "en"):
                current_lang = lang
            blocks.append({"type": tag, "html": f"<{tag}>{inner}</{tag}>", "raw_text": raw, "lang": lang})
            i += 1
            continue

        # ── Fenced code block ─────────────────────────────────────────────────
        if stripped.startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # closing ```
            code_content = "\n".join(code_lines)
            blocks.append({
                "type": "pre",
                "html": f"<pre><code>{esc(code_content)}</code></pre>",
                "raw_text": code_content,
                "lang": "common",
            })
            continue

        # ── Blockquote ────────────────────────────────────────────────────────
        if stripped.startswith("> "):
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith("> "):
                quote_lines.append(lines[i].strip()[2:])
                i += 1
            content = " ".join(quote_lines)
            inner = render_inline(content)
            raw = re.sub(r"<[^>]+>", "", inner)
            lang = detect_lang(raw, current_lang)
            if lang in ("ko", "ja", "en"):
                current_lang = lang
            blocks.append({
                "type": "blockquote",
                "html": f"<blockquote>{inner}</blockquote>",
                "raw_text": raw,
                "lang": lang,
            })
            continue

        # ── Unordered list (with nested sub-items) ──────────────────────────
        if re.match(r"^[-*+]\s+", stripped):

            def build_ul(lines_list, start, base_indent):
                """Recursively build <ul> html and collect raw text."""
                html_parts = []
                raw_parts = []
                idx = start
                while idx < len(lines_list):
                    ln = lines_list[idx]
                    if not re.match(r"^(\s*)[-*+]\s+", ln):
                        break
                    indent = len(ln) - len(ln.lstrip())
                    if indent < base_indent:
                        break  # de-indent: return to parent
                    if indent > base_indent:
                        # deeper indent: nest
                        sub_html, sub_raw, idx = build_ul(lines_list, idx, indent)
                        if html_parts:
                            # attach nested ul inside last <li>
                            html_parts[-1] = html_parts[-1][:-5] + sub_html + "</li>"
                            raw_parts[-1] += " " + sub_raw
                        else:
                            html_parts.append(sub_html)
                            raw_parts.append(sub_raw)
                        continue
                    item_text = re.sub(r"^\s*[-*+]\s+", "", ln).strip()
                    inner_item = render_inline(item_text)
                    raw_item = re.sub(r"<[^>]+>", "", inner_item)
                    html_parts.append(f"<li>{inner_item}</li>")
                    raw_parts.append(raw_item)
                    idx += 1
                return f"<ul>{''.join(html_parts)}</ul>", " ".join(raw_parts), idx

            base = len(lines[i]) - len(lines[i].lstrip())
            ul_html, raw_all, i = build_ul(lines, i, base)
            lang = detect_lang(raw_all, current_lang)
            if lang in ("ko", "ja", "en"):
                current_lang = lang
            blocks.append({
                "type": "ul",
                "html": ul_html,
                "raw_text": raw_all,
                "lang": lang,
            })
            continue

        # ── Ordered list ──────────────────────────────────────────────────────
        if re.match(r"^\d+\.\s+", stripped):
            items = []
            raw_parts = []
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                item_text = re.sub(r"^\s*\d+\.\s+", "", lines[i]).strip()
                inner = render_inline(item_text)
                raw = re.sub(r"<[^>]+>", "", inner)
                items.append(f"<li>{inner}</li>")
                raw_parts.append(raw)
                i += 1
            raw_all = " ".join(raw_parts)
            lang = detect_lang(raw_all, current_lang)
            if lang in ("ko", "ja", "en"):
                current_lang = lang
            blocks.append({
                "type": "ol",
                "html": f"<ol>{''.join(items)}</ol>",
                "raw_text": raw_all,
                "lang": lang,
            })
            continue

        # ── Table ─────────────────────────────────────────────────────────────
        if "|" in stripped and stripped.startswith("|"):
            table_lines = []
            while i < len(lines) and "|" in lines[i] and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            # Remove separator row (---|---)
            table_lines = [l for l in table_lines if not re.match(r"^\|[-:\s|]+\|$", l)]
            rows = []
            for li, tl in enumerate(table_lines):
                cells = [c.strip() for c in tl.strip("|").split("|")]
                if li == 0:
                    row_html = "<tr>" + "".join(f"<th>{render_inline(c)}</th>" for c in cells) + "</tr>"
                else:
                    row_html = "<tr>" + "".join(f"<td>{render_inline(c)}</td>" for c in cells) + "</tr>"
                rows.append(row_html)
            raw_all = " ".join(re.sub(r"<[^>]+>", "", r) for r in rows)
            lang = detect_lang(raw_all, current_lang)
            if lang in ("ko", "ja", "en"):
                current_lang = lang
            blocks.append({
                "type": "table",
                "html": f"<table>{''.join(rows)}</table>",
                "raw_text": raw_all,
                "lang": lang,
            })
            continue

        # ── Empty line ────────────────────────────────────────────────────────
        if not stripped:
            i += 1
            continue

        # ── Paragraph ─────────────────────────────────────────────────────────
        para_lines = []
        while i < len(lines) and lines[i].strip() and not re.match(
            r"^(#{1,6}\s|[-*+]\s|\d+\.\s|>|```|[-*_]{3,}|\|)", lines[i].strip()
        ):
            para_lines.append(lines[i].strip())
            i += 1

        content = " ".join(para_lines)
        inner = render_inline(content)
        raw = re.sub(r"<[^>]+>", "", inner)
        lang = detect_lang(raw, current_lang)
        if lang in ("ko", "ja", "en"):
            current_lang = lang
        blocks.append({"type": "p", "html": f"<p>{inner}</p>", "raw_text": raw, "lang": lang})

    return blocks


# ── UI helpers ────────────────────────────────────────────────────────────────

def html_text(s: str) -> str:
    return esc(s)


def icon_for_kind(kind: str) -> str:
    return {"support": "support_agent", "privacy": "description", "terms": "gavel"}.get(kind, "article")


def app_visuals(app_id: str):
    if app_id == "snow":
        return {
            "hero_label": "Snow Record Docs",
            "hero_title": "Snow Record Documentation",
            "hero_desc": "Support, privacy, and terms documents for Snow Record.",
            "icon": "ac_unit",
            "image": "https://lh3.googleusercontent.com/aida-public/AB6AXuDyDZ0qbrbt01FoxxipkYWM1kECRJwe0sWoVy9Bx2HZeCGxYeDTdXFhy4KfYlgXJ1AWlHPNyNxFan8lNOAHXB4ZVMwTJiIMGwJfCymmt6Y_srY9-AoWDFbq3DgR4kCkI_Hy8VFTw8uQbpMiLgHMJnpMZ3zErs5DdG6bkA_LAkQ5ZTUg3vjgsdgm1ZuMP_wkFHCig7XiOmJclO8DTVPfskTMfrPgJqXjnqqr8-53Fgob0r3k9rPIAGAIZ-JXwk1QKScItJHJgdHzhBVY",
        }
    if app_id == "ssak":
        return {
            "hero_label": "SSAK Docs",
            "hero_title": "SSAK Documentation",
            "hero_desc": "Legal and support documentation for SSAK: Photo Cleaner.",
            "icon": "cleaning_services",
            "image": "https://lh3.googleusercontent.com/aida-public/AB6AXuCGkhQMv5cUhNBfWTgZStHRpdoALN3_rdRvqHMdum2mCs_wazRU8Gzb7lU0oJkasuiXhnakH7cL-Qx4t41bVp6QYyasRdKtLFbhqnHMo3jsKTVd5AOJwTo-yFFLHJyFYbDQfx1K3eAaYFxkzDCHc8oHYDHX7WJPi2d9p_8d5T-VnvV3okqcxDVUI-EhSvMri913rbL5Ao61gW6ZCjhhl7QXqdranw-_iT_K8GyK_Jtikd_elO3D8EGGSaXIQ8l1jF5bfSA3X-tg0FMB",
        }
    return {
        "hero_label": "Wayin Korea Docs",
        "hero_title": "Wayin Korea Documentation",
        "hero_desc": "Policies and terms for Wayin Korea services.",
        "icon": "map",
        "image": "https://lh3.googleusercontent.com/aida-public/AB6AXuBg9CkiZLs4Ejj9witNwnSJJl6ARUjzxsX01K0WuttH16qHGztp8QdnqbD9GGzrQtZ2G2gBs67tCUd4E0HrkhTFqJEzfFTkSZPoh25zB5gT-ctFigq_FvXGY9oH_O0KPApigg6DFxkO4KSWJjBLhc1-IbVK09RSSbBKhjZBkfSBPc0qnz8cuHfabf_UqzEzGjZ605WHTwewR7JzVCnox3dhg8cbcrB8BDb6VIZCciG8KXhyAkbh_jI-p9dCe4ArdEjAntsDFQG8BOVr",
    }


# ── Page renderers ────────────────────────────────────────────────────────────

TAILWIND_CONFIG = """
tailwind.config = {
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        "primary": "#75f21c",
        "background-light": "#f7f8f5",
        "background-dark": "#172210",
      },
      fontFamily: {
        "display": ["Inter", "sans-serif"]
      },
      borderRadius: {"DEFAULT": "0.25rem", "lg": "0.5rem", "xl": "0.75rem", "full": "9999px"},
    },
  },
}
"""

SCROLLBAR_STYLE = """
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #172210; }
::-webkit-scrollbar-thumb { background: #33442a; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #455a3b; }

/* Notion-like document styles */
.notion-doc h1 { font-size: 2rem; font-weight: 800; margin: 1.5rem 0 0.75rem; line-height: 1.2; }
.notion-doc h2 { font-size: 1.4rem; font-weight: 700; margin: 1.75rem 0 0.5rem; line-height: 1.3; }
.notion-doc h3 { font-size: 1.15rem; font-weight: 700; margin: 1.5rem 0 0.4rem; line-height: 1.3; }
.notion-doc h4 { font-size: 1rem; font-weight: 600; margin: 1.25rem 0 0.3rem; color: #d9ffc5; }
.notion-doc p { margin: 0.5rem 0 0.75rem; line-height: 1.75; }
.notion-doc ul { list-style: disc; padding-left: 1.5rem; margin: 0.5rem 0 0.75rem; }
.notion-doc ol { list-style: decimal; padding-left: 1.5rem; margin: 0.5rem 0 0.75rem; }
.notion-doc li { margin: 0.25rem 0; line-height: 1.7; }
.notion-doc li::marker { color: #75f21c; }
.notion-doc strong { font-weight: 700; color: #f0f4ee; }
.notion-doc em { font-style: italic; color: #d0dcc8; }
.notion-doc code {
  font-family: "Fira Code", monospace;
  font-size: 0.85em;
  background: rgba(117, 242, 28, 0.1);
  color: #9ced4e;
  padding: 0.1em 0.4em;
  border-radius: 4px;
}
.notion-doc pre {
  background: #0d1209;
  border: 1px solid #2b3d27;
  border-radius: 8px;
  padding: 1rem;
  overflow-x: auto;
  margin: 1rem 0;
}
.notion-doc pre code { background: none; padding: 0; color: #b8e6a0; }
.notion-doc blockquote {
  border-left: 3px solid rgba(117, 242, 28, 0.5);
  padding: 0.5rem 1rem;
  margin: 1rem 0;
  background: rgba(117, 242, 28, 0.05);
  border-radius: 0 6px 6px 0;
  color: #b8d4ae;
}
.notion-doc hr {
  border: 0;
  border-top: 1px solid #2b3d27;
  margin: 1.5rem 0;
}
.notion-doc table {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
  font-size: 0.9rem;
}
.notion-doc th {
  background: rgba(117, 242, 28, 0.1);
  color: #d9ffc5;
  font-weight: 700;
  padding: 0.5rem 0.75rem;
  border: 1px solid #2b3d27;
  text-align: left;
}
.notion-doc td {
  padding: 0.5rem 0.75rem;
  border: 1px solid #2b3d27;
  color: #c0d4b8;
}
.notion-doc a { color: #9ced4e; text-decoration: none; }
.notion-doc a:hover { text-decoration: underline; }
"""

LANG_SCRIPT = """
<script>
document.addEventListener("DOMContentLoaded", function() {
  const tabContainers = document.querySelectorAll("[data-default-lang]");
  tabContainers.forEach(function(tabs) {
    const buttons = Array.from(tabs.querySelectorAll("[data-lang-target]"));
    const panel = tabs.closest(".doc-wrap");
    const blocks = panel ? Array.from(panel.querySelectorAll("[data-lang]")) : [];
    const defaultLang = tabs.dataset.defaultLang || "all";

    function setActive(lang) {
      buttons.forEach(function(btn) {
        const active = btn.dataset.langTarget === lang;
        btn.classList.toggle("lang-btn-active", active);
      });
      blocks.forEach(function(block) {
        const bl = block.dataset.lang;
        const visible = lang === "all" || bl === "common" || bl === lang;
        block.style.display = visible ? "" : "none";
      });
    }

    buttons.forEach(function(btn) {
      btn.addEventListener("click", function() { setActive(btn.dataset.langTarget); });
    });
    setActive(defaultLang);
  });

  // Print button
  const printBtn = document.getElementById("print-btn");
  if (printBtn) printBtn.addEventListener("click", function() { window.print(); });
});
</script>
"""


def render_lang_tabs(available_langs: set) -> str:
    order = [("en", "English"), ("ko", "한국어"), ("ja", "日本語"), ("all", "All")]
    default = "en" if "en" in available_langs else (sorted(available_langs)[0] if available_langs else "all")
    buttons = []
    for code, label in order:
        if code == "all" or code in available_langs:
            active_cls = " lang-btn-active" if code == default else ""
            buttons.append(
                f'<button type="button" class="lang-btn{active_cls}" data-lang-target="{code}">{esc(label)}</button>'
            )
    html = f'<div class="lang-tabs" data-default-lang="{default}">'
    html += "".join(buttons) + "</div>"
    return html, default


LANG_TAB_CSS = """
.lang-tabs { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px; }
.lang-btn {
  border: 1px solid #37522f;
  background: #141f12;
  color: #bfd2b7;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
  padding: 6px 16px;
  cursor: pointer;
  transition: all 0.15s;
}
.lang-btn:hover { border-color: rgba(117,242,28,0.5); color: #d9ffc3; }
.lang-btn.lang-btn-active {
  border-color: rgba(117,242,28,0.6);
  background: rgba(117,242,28,0.15);
  color: #d9ffc3;
}
"""


def render_doc_page(doc_key: str, blocks: list[dict]) -> str:
    meta = DOCS[doc_key]
    app = APPS[meta["app"]] if meta["app"] else None

    # TOC from h2/h3 blocks
    toc = []
    section_count = 0
    for blk in blocks:
        if blk["type"] in ("h2", "h3") and blk["raw_text"]:
            section_count += 1
            sid = f"sec-{section_count}"
            blk["id"] = sid
            toc.append((sid, blk["raw_text"][:80]))

    # Detect available languages
    available_langs = {b["lang"] for b in blocks if b["lang"] in ("en", "ko", "ja")}
    show_tabs = len(available_langs) >= 2

    # Render HTML blocks
    content_parts = []
    for blk in blocks:
        lang = blk["lang"]
        html = blk["html"]

        # Add id to heading if in TOC
        if blk.get("id"):
            html = html.replace(f"<{blk['type']}>", f'<{blk["type"]} id="{blk["id"]}">', 1)

        # Apply type-specific classes
        if blk["type"] == "h2":
            html = html.replace(f'<h2', '<h2 class="notion-h2"', 1)
        elif blk["type"] == "h3":
            html = html.replace(f'<h3', '<h3 class="notion-h3"', 1)

        content_parts.append(f'<div data-lang="{lang}">{html}</div>')

    wrapped = "\n".join(content_parts)
    tabs_html, default_lang = render_lang_tabs(available_langs) if show_tabs else ("", "en")

    # Update text (find date)
    update_text = "See document for effective date"
    for blk in blocks:
        m = re.search(
            r"(Last Updated|Effective Date|최종 수정일|시행일|最終更新日)\s*[:\：]\s*([^\n<]{3,40})",
            blk["raw_text"],
            re.IGNORECASE,
        )
        if m:
            update_text = f"{m.group(1)}: {m.group(2).strip()}"
            break

    # Breadcrumb & related
    if app:
        breadcrumb_mid = f'<a class="hover:text-primary transition-colors" href="{esc(app["hub"])}">{esc(app["name"])}</a>'
        related_cards = []
        for sibling_key in app["docs"]:
            if sibling_key == doc_key:
                continue
            s = DOCS[sibling_key]
            related_cards.append(
                f'''<a class="group block p-4 rounded-lg bg-neutral-100 dark:bg-[#1a2415] border border-transparent hover:border-primary/50 transition-all" href="{esc(s["out"])}">
<div class="flex items-start justify-between">
<span class="material-symbols-outlined text-slate-400 dark:text-[#5a6a50] group-hover:text-primary mb-2">{icon_for_kind(s["kind"])}</span>
<span class="material-symbols-outlined text-[16px] text-slate-400 -rotate-45 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform">arrow_forward</span>
</div>
<h5 class="text-slate-900 dark:text-white font-medium text-sm mb-1">{esc(s["label"])}</h5>
<p class="text-xs text-slate-500 dark:text-[#a8ba9c]">{esc(s["title"])}</p></a>'''
            )
        related_html = "".join(related_cards[:2])
    else:
        breadcrumb_mid = '<a class="hover:text-primary transition-colors" href="index.html">Company</a>'
        related_html = ""

    toc_html = "".join(
        f'<li><a class="block pl-4 text-sm font-medium text-slate-600 dark:text-[#a8ba9c] hover:text-slate-900 dark:hover:text-white border-l-2 border-transparent hover:border-[#4a5a40] transition-colors" href="#{esc(tid)}">{esc(label)}</a></li>'
        for tid, label in toc
    )

    return f"""<!DOCTYPE html>
<html class="dark" lang="en"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>{esc(meta["title"])} - FACTORY 471</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<script id="tailwind-config">{TAILWIND_CONFIG}</script>
<style>
{SCROLLBAR_STYLE}
{LANG_TAB_CSS}
</style>
</head>
<body class="font-display bg-background-light dark:bg-background-dark text-slate-900 dark:text-slate-100 min-h-screen flex flex-col">
<header class="sticky top-0 z-50 w-full border-b border-neutral-200 dark:border-[#2f3928] bg-background-light/95 dark:bg-background-dark/95 backdrop-blur-md">
<div class="px-6 md:px-10 py-3 flex items-center justify-between mx-auto max-w-[1400px]">
<div class="flex items-center gap-8">
<a class="flex items-center gap-3 group" href="index.html">
<div class="size-8 text-primary"><svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg"><g><path clip-rule="evenodd" d="M24 0.757355L47.2426 24L24 47.2426L0.757355 24L24 0.757355ZM21 35.7574V12.2426L9.24264 24L21 35.7574Z" fill="currentColor" fill-rule="evenodd"></path></g></svg></div>
<h2 class="text-slate-900 dark:text-white text-lg font-bold tracking-tight">FACTORY 471</h2></a>
<nav class="hidden md:flex items-center gap-8">
<a class="text-slate-600 dark:text-[#a8ba9c] hover:text-primary transition-colors text-sm font-medium" href="index.html">Apps</a>
<a class="text-slate-600 dark:text-[#a8ba9c] hover:text-primary transition-colors text-sm font-medium" href="about.html">Studio</a>
</nav></div>
<div class="flex items-center gap-4">
<button id="print-btn" class="hidden sm:flex p-2 rounded-lg hover:bg-neutral-200 dark:hover:bg-[#2f3928] text-slate-500 dark:text-[#a8ba9c] transition-colors" title="Print"><span class="material-symbols-outlined">print</span></button>
<a class="bg-primary hover:bg-primary/90 text-background-dark text-sm font-bold px-5 py-2.5 rounded-lg transition-colors" href="{esc(meta["notion_url"])}" target="_blank" rel="noopener noreferrer">View on Notion</a>
</div></div></header>
<main class="flex-grow w-full px-6 md:px-10 py-8 mx-auto max-w-[1400px] doc-wrap">
<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-[#a8ba9c] mb-6">
<a class="hover:text-primary transition-colors" href="index.html">Home</a>
<span class="material-symbols-outlined text-[16px]">chevron_right</span>
{breadcrumb_mid}
<span class="material-symbols-outlined text-[16px]">chevron_right</span>
<span class="text-slate-900 dark:text-white font-medium">{esc(meta["label"])}</span></nav>
<div class="grid grid-cols-1 lg:grid-cols-12 gap-12">
<div class="lg:col-span-8 xl:col-span-9 flex flex-col gap-8">
<div class="border-b border-neutral-200 dark:border-[#2f3928] pb-8">
<h1 class="text-4xl md:text-5xl font-black tracking-tight text-slate-900 dark:text-white mb-4">{esc(meta["label"])}</h1>
<div class="flex flex-wrap items-center justify-between gap-4">
<p class="text-slate-500 dark:text-[#a8ba9c] font-medium">{esc(update_text)}</p>
<a class="p-2 rounded-lg hover:bg-neutral-200 dark:hover:bg-[#2f3928] text-slate-500 dark:text-[#a8ba9c] transition-colors" title="Open on Notion" href="{esc(meta["notion_url"])}" target="_blank" rel="noopener noreferrer"><span class="material-symbols-outlined">open_in_new</span></a>
</div></div>
{tabs_html}
<article class="notion-doc">
{wrapped}
</article>
<div class="mt-12 pt-8 border-t border-neutral-200 dark:border-[#2f3928]">
<h3 class="text-lg font-bold text-slate-900 dark:text-white mb-4">Was this document helpful?</h3>
<div class="flex gap-4">
<button class="flex items-center gap-2 px-4 py-2 rounded-lg border border-neutral-300 dark:border-[#2f3928] hover:border-primary text-slate-600 dark:text-[#a8ba9c] hover:text-primary transition-all group"><span class="material-symbols-outlined group-hover:text-primary transition-colors">thumb_up</span><span>Yes</span></button>
<button class="flex items-center gap-2 px-4 py-2 rounded-lg border border-neutral-300 dark:border-[#2f3928] hover:border-red-400 text-slate-600 dark:text-[#a8ba9c] hover:text-red-400 transition-all group"><span class="material-symbols-outlined group-hover:text-red-400 transition-colors">thumb_down</span><span>No</span></button>
</div></div></div>
<aside class="hidden lg:block lg:col-span-4 xl:col-span-3">
<div class="sticky top-24 space-y-8">
<div class="bg-neutral-100 dark:bg-[#1a2415] rounded-xl p-6 border border-neutral-200 dark:border-[#2f3928]">
<h4 class="text-sm font-bold uppercase tracking-wider text-slate-500 dark:text-[#a8ba9c] mb-4">On this page</h4>
<ul class="space-y-3 relative">{toc_html}</ul></div>
{f'<div><h4 class="text-sm font-bold uppercase tracking-wider text-slate-500 dark:text-[#a8ba9c] mb-4">Related Documents</h4><div class="space-y-3">{related_html}</div></div>' if related_html else ""}
<div class="relative overflow-hidden rounded-xl bg-gradient-to-br from-[#2f3928] to-[#1a2415] p-6 border border-[#3d4a35]">
<div class="relative z-10"><h4 class="text-white font-bold mb-2">Have questions?</h4><p class="text-sm text-[#a8ba9c] mb-4">Our support team is available to help clarify any policy concerns.</p>
<a href="about.html" class="block w-full py-2 bg-primary/20 hover:bg-primary/30 text-primary border border-primary/50 rounded-lg text-sm font-bold transition-colors text-center">Contact Support</a></div>
<div class="absolute -right-4 -bottom-8 w-24 h-24 bg-primary/10 rounded-full blur-xl"></div></div>
</div></aside></div></main>
<footer class="mt-auto border-t border-neutral-200 dark:border-[#2f3928] bg-background-light dark:bg-background-dark py-12">
<div class="px-6 md:px-10 mx-auto max-w-[1400px]">
<div class="flex flex-col md:flex-row justify-between items-center gap-6">
<div class="flex items-center gap-2 text-slate-500 dark:text-[#a8ba9c] text-sm"><span>&copy; 2026 FACTORY 471. All rights reserved.</span></div>
<div class="flex gap-6">
<a class="text-slate-500 dark:text-[#a8ba9c] hover:text-primary transition-colors text-sm" href="{esc(DOCS["snow-privacy"]["out"])}">Privacy</a>
<a class="text-slate-500 dark:text-[#a8ba9c] hover:text-primary transition-colors text-sm" href="{esc(DOCS["snow-terms"]["out"])}">Terms</a>
<a class="text-slate-500 dark:text-[#a8ba9c] hover:text-primary transition-colors text-sm" href="index.html">Sitemap</a>
</div></div></div></footer>
{LANG_SCRIPT}
</body></html>"""


def render_hub_page(app_id: str, lang_map: dict) -> str:
    app = APPS[app_id]
    visual = app_visuals(app_id)
    cards = []
    for key in app["docs"]:
        meta = DOCS[key]
        langs = lang_map.get(key, set())
        lang_badge = "".join(
            f'<span class="text-[10px] px-1.5 py-0.5 rounded bg-slate-200 dark:bg-[#384530] text-slate-600 dark:text-slate-300 font-bold">{code.upper()}</span>'
            for code in sorted(langs)
        ) or '<span class="text-[10px] px-1.5 py-0.5 rounded bg-slate-200 dark:bg-[#384530] text-slate-600 dark:text-slate-300 font-bold">EN</span>'
        cards.append(
            f"""
<a class="flex items-center justify-between p-3 rounded-lg bg-slate-50 dark:bg-[#232e1c] hover:bg-slate-100 dark:hover:bg-[#2f3928] group/item transition-colors" href="{esc(meta["out"])}">
  <div class="flex items-center gap-3">
    <span class="material-symbols-outlined text-slate-400 group-hover/item:text-primary text-sm">{icon_for_kind(meta["kind"])}</span>
    <span class="text-sm font-medium text-slate-700 dark:text-slate-200">{esc(meta["label"])}</span>
  </div>
  <div class="flex gap-1">{lang_badge}</div>
</a>
"""
        )

    return f"""<!DOCTYPE html>
<html class="dark" lang="en"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>{esc(app["name"])} Documentation Hub - FACTORY 471</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<script id="tailwind-config">{TAILWIND_CONFIG}</script>
<style>
{SCROLLBAR_STYLE}
.bg-grid-pattern {{
  background-image: linear-gradient(to right, #2f3928 1px, transparent 1px),
  linear-gradient(to bottom, #2f3928 1px, transparent 1px);
  background-size: 40px 40px;
}}
</style>
</head>
<body class="font-display bg-background-light dark:bg-background-dark text-slate-900 dark:text-slate-100 min-h-screen flex flex-col">
<header class="flex items-center justify-between whitespace-nowrap border-b border-solid border-slate-200 dark:border-[#2f3928] px-6 py-4 lg:px-10 sticky top-0 z-50 bg-background-light/80 dark:bg-background-dark/80 backdrop-blur-md">
<div class="flex items-center gap-4 text-slate-900 dark:text-white">
<div class="size-6 text-primary"><svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg"><g><path clip-rule="evenodd" d="M24 0.757355L47.2426 24L24 47.2426L0.757355 24L24 0.757355ZM21 35.7574V12.2426L9.24264 24L21 35.7574Z" fill="currentColor" fill-rule="evenodd"></path></g></svg></div>
<h2 class="text-lg font-bold leading-tight tracking-[-0.015em]">FACTORY 471</h2></div>
<div class="hidden md:flex flex-1 justify-end gap-8 items-center">
<div class="flex items-center gap-9">
<a class="text-slate-600 dark:text-slate-300 hover:text-primary transition-colors text-sm font-medium leading-normal" href="index.html">Apps</a>
<a class="text-slate-600 dark:text-slate-300 hover:text-primary transition-colors text-sm font-medium leading-normal" href="about.html">Studio</a>
</div>
<a class="flex min-w-[84px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-10 px-6 bg-primary text-background-dark text-sm font-bold leading-normal tracking-[0.015em] hover:opacity-90 transition-opacity" href="index.html"><span class="truncate">Home</span></a>
</div></header>
<div class="w-full border-b border-slate-200 dark:border-[#2f3928] bg-slate-50 dark:bg-[#1a2614]">
<div class="max-w-7xl mx-auto px-6 lg:px-10 py-3 flex flex-wrap items-center gap-2">
<a class="text-slate-500 dark:text-[#a8ba9c] text-sm font-medium hover:text-primary transition-colors" href="index.html">Home</a>
<span class="material-symbols-outlined text-slate-400 text-xs">chevron_right</span>
<span class="text-slate-900 dark:text-white text-sm font-bold">{esc(app["name"])}</span>
</div></div>
<div class="relative w-full border-b border-slate-200 dark:border-[#2f3928]">
<div class="absolute inset-0 bg-grid-pattern opacity-[0.05] dark:opacity-[0.15] pointer-events-none"></div>
<div class="relative max-w-7xl mx-auto px-6 lg:px-10 py-20 lg:py-24">
<div class="max-w-3xl flex flex-col gap-6">
<div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 w-fit">
<span class="material-symbols-outlined text-primary text-sm">{visual["icon"]}</span>
<span class="text-xs font-bold text-primary uppercase tracking-wider">{esc(visual["hero_label"])}</span>
</div>
<h1 class="text-slate-900 dark:text-white text-5xl md:text-6xl font-black leading-tight tracking-[-0.033em]">{esc(visual["hero_title"])}<span class="text-primary">.</span></h1>
<p class="text-slate-600 dark:text-slate-400 text-lg md:text-xl font-normal leading-relaxed max-w-2xl">{esc(visual["hero_desc"])}</p>
</div></div></div>
<div class="flex-1 bg-slate-50 dark:bg-[#141811]">
<div class="max-w-7xl mx-auto px-6 lg:px-10 py-16">
<div class="flex items-center justify-between mb-10">
<h2 class="text-2xl md:text-3xl font-bold text-slate-900 dark:text-white tracking-tight">Select a Document</h2>
<span class="text-sm text-slate-500 dark:text-slate-400 hidden sm:block">Showing {len(app["docs"])} documents</span>
</div>
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
{''.join(
    f'''<div class="group relative flex flex-col bg-white dark:bg-[#1a2614] border border-slate-200 dark:border-[#2f3928] rounded-xl overflow-hidden hover:border-primary/50 transition-all duration-300 shadow-sm hover:shadow-lg hover:shadow-primary/5">
<div class="h-32 bg-slate-100 dark:bg-[#232e1c] relative overflow-hidden">
<img alt="{esc(app["name"])} document cover" class="w-full h-full object-cover opacity-60 group-hover:scale-105 transition-transform duration-500" src="{visual["image"]}"/>
<div class="absolute inset-0 bg-gradient-to-t from-[#1a2614] to-transparent opacity-0 dark:opacity-100"></div>
</div>
<div class="p-6 flex flex-col flex-1 relative">
<div class="size-16 rounded-xl bg-slate-200 dark:bg-[#2f3928] -mt-12 mb-4 border-4 border-white dark:border-[#1a2614] shadow-md flex items-center justify-center relative z-10">
<span class="material-symbols-outlined text-3xl text-primary">{icon_for_kind(DOCS[k]["kind"])}</span>
</div>
<h3 class="text-xl font-bold text-slate-900 dark:text-white mb-2">{esc(DOCS[k]["label"])}</h3>
<p class="text-sm text-slate-500 dark:text-slate-400 mb-4">{esc(DOCS[k]["title"])}</p>
<div class="mt-auto"><a href="{esc(DOCS[k]["out"])}" class="w-full py-2.5 rounded-lg border border-primary text-primary hover:bg-primary hover:text-background-dark font-bold text-sm transition-all flex items-center justify-center gap-2">Open Document<span class="material-symbols-outlined text-lg">arrow_forward</span></a></div>
</div></div>'''
    for k in app["docs"]
)}
</div></div></div>
<footer class="border-t border-slate-200 dark:border-[#2f3928] py-8 px-6 lg:px-10 bg-white dark:bg-[#1a2614]">
<div class="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
<div class="flex items-center gap-2 text-slate-900 dark:text-white">
<div class="size-4 text-primary"><svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg"><g><path clip-rule="evenodd" d="M24 0.757355L47.2426 24L24 47.2426L0.757355 24L24 0.757355ZM21 35.7574V12.2426L9.24264 24L21 35.7574Z" fill="currentColor" fill-rule="evenodd"></path></g></svg></div>
<span class="text-sm font-bold">FACTORY 471</span></div>
<div class="text-xs text-slate-500 dark:text-slate-400 text-center md:text-right"><p>&copy; 2026 FACTORY 471. All rights reserved.</p></div>
</div></footer>
</body></html>"""


def patch_index():
    path = ROOT / "index.html"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    text = text.replace('href="#">About</a>', 'href="about.html">About</a>')
    text = text.replace('href="#">About Us</a>', 'href="about.html">About Us</a>')
    path.write_text(text, encoding="utf-8")


# Regex to detect Notion language-selector lines like:
# [🇺🇸 **English**](url) | [🇰🇷 **한국어**](url) | [🇯🇵 **日本語**](url)
_LANG_SELECTOR_RE = re.compile(
    r"^\s*\[.*?(English|한국어|日本語).*?\]\(https?://[^\)]+\)"  # starts with [lang](url)
    r"(\s*\|?\s*\[.*?\]\(https?://[^\)]+\))*\s*$",             # more | [...](url) parts
    re.IGNORECASE,
)


def load_md(doc_key: str) -> list[dict]:
    """Find and parse the markdown file for a given doc key."""
    meta = DOCS[doc_key]
    # md_root=True → file is in project root, not notion_exports/
    search_dir = ROOT if meta.get("md_root") else EXPORTS_DIR
    candidates = list(search_dir.glob(meta["md_glob"]))
    if not candidates:
        print(f"  [WARN] No markdown file found for {doc_key} in {search_dir} (pattern: {meta['md_glob']})")
        return []
    md_path = candidates[0]
    text = md_path.read_text(encoding="utf-8")

    # Preprocess: strip title line and Notion language-selector lines
    lines = text.splitlines()
    cleaned = []
    for li, line in enumerate(lines):
        # Remove the first H1 (page title — already shown in page <h1>)
        if li == 0 and line.startswith("# "):
            continue
        # Remove Notion language selector lines (e.g. [🇺🇸 English](url) | [🇰🇷 한국어](url))
        if _LANG_SELECTOR_RE.match(line):
            continue
        cleaned.append(line)

    text = "\n".join(cleaned)
    blocks = md_to_html_blocks(text)
    print(f"  [{doc_key}] {md_path.name} → {len(blocks)} blocks")
    return blocks


def main():
    lang_map = {}

    print("Building document pages...")
    for key, meta in DOCS.items():
        blocks = load_md(key)
        langs = {b["lang"] for b in blocks if b["lang"] in ("en", "ko", "ja")}
        lang_map[key] = langs
        html = render_doc_page(key, blocks)
        out_path = ROOT / meta["out"]
        out_path.write_text(html, encoding="utf-8")
        print(f"  → Written: {meta['out']}")

    print("\nBuilding hub pages...")
    for app_id in APPS:
        html = render_hub_page(app_id, lang_map)
        out_path = ROOT / APPS[app_id]["hub"]
        out_path.write_text(html, encoding="utf-8")
        print(f"  → Written: {APPS[app_id]['hub']}")

    patch_index()
    print("\nDone! ✅")


if __name__ == "__main__":
    main()
