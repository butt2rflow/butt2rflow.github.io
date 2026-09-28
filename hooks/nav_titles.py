"""Short sidebar labels.

The left navigation uses page.title. Long "Title — subtitle" titles wrap onto
three lines, so this hook shortens the nav label only:
  - front matter `nav_title:` wins if present
  - otherwise the part of `title:` before " — "
Explicit labels given in mkdocs.yml nav are left alone. The <title> tag uses
page.meta.title (Material), so it keeps the full title.
"""

SEP = " — "


def on_page_markdown(markdown, page, config, files):
    meta_title = page.meta.get("title")
    if not meta_title or page.title != meta_title:
        return markdown  # no front-matter title, or an explicit nav label
    short = page.meta.get("nav_title") or meta_title.split(SEP)[0]
    page.title = short.strip()
    return markdown
