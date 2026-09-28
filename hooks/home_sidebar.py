"""Home-page sidebar: recent posts + category list.

The home tab's sidebar only holds "Home", so it looks empty. At render time
(when every page's front matter is loaded) this hook appends a hidden block to
the homepage content; assets/home-sidebar.js moves it into the left sidebar.

- Recent: newest `date:` first, at most one post per nav section (so a series
  published on one day doesn't fill the list), ties broken by later nav order.
- Categories: every nav section under the top-level tabs, linking to its first
  page. Titles come from the (translated) nav, labels from nav_titles.py.
"""

import datetime
import html

RECENT = 5
LABELS = {
    "ko": ("최근 글", "카테고리"),
    "en": ("Recent posts", "Categories"),
}


def _first_page(item):
    if item.is_page:
        return item
    for child in item.children or []:
        page = _first_page(child)
        if page:
            return page
    return None


def _walk(items, section=None):
    """Yield (page, nearest section title) in nav order."""
    for item in items:
        if item.is_page:
            yield item, section
        elif item.is_section:
            yield from _walk(item.children, item.title)


def _as_date(value):
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    try:
        return datetime.date.fromisoformat(str(value))
    except ValueError:
        return None


def _href(page_from, page_to):
    # relative link, same as MkDocs' own nav links
    return page_to.url_relative_to(page_from) if hasattr(page_to, "url_relative_to") else page_to.url


def on_page_context(context, page, config, nav):
    if page.url not in ("", "en/"):  # KO and EN homepages (i18n suffix build)
        return context
    lang = "en" if page.url.startswith("en/") else "ko"
    recent_label, cat_label = LABELS[lang]

    ordered = list(_walk(nav.items))
    dated = []
    for idx, (p, sec) in enumerate(ordered):
        d = _as_date(p.meta.get("date")) if p.meta else None
        if d and p.url not in ("", "en/"):
            dated.append((d, idx, p, sec))
    dated.sort(key=lambda t: (t[0], t[1]), reverse=True)
    recent, seen = [], set()
    for d, _, p, sec in dated:
        if sec in seen:
            continue
        seen.add(sec)
        recent.append((d, p, sec))
        if len(recent) == RECENT:
            break

    out = ['<div id="home-sidebar-src" class="home-side" hidden>']
    out.append(f'<div class="home-side__title">{html.escape(recent_label)}</div><ul class="home-side__recent">')
    for d, p, sec in recent:
        meta = f"{sec} · {d:%m-%d}" if sec else f"{d:%m-%d}"
        out.append(
            f'<li><a href="{html.escape(_href(page, p))}">{html.escape(p.title)}</a>'
            f'<span class="home-side__meta">{html.escape(meta)}</span></li>'
        )
    out.append("</ul>")
    out.append(f'<div class="home-side__title">{html.escape(cat_label)}</div>')
    for top in nav.items:
        if not top.is_section:
            continue
        cats = [c for c in top.children if c.is_section]
        if not cats:
            continue
        out.append(f'<div class="home-side__tab">{html.escape(top.title)}</div><ul class="home-side__cats">')
        for c in cats:
            first = _first_page(c)
            if first:
                out.append(f'<li><a href="{html.escape(_href(page, first))}">{html.escape(c.title)}</a></li>')
        out.append("</ul>")
    out.append("</div>")
    page.content = (page.content or "") + "\n".join(out)
    return context
