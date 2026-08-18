#!/usr/bin/env python3
"""
Assembles the static pages.

Each file in tools/pages/<slug>.html holds only the page body: a front-matter
block of `key: value` lines, a blank line, then the markup that goes inside
<main>. This script wraps that in the shared shell (head, icon sprite, header,
footer) and writes <slug>.html to the site root.

Run after editing any page or the shell:  python3 tools/build.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = Path(__file__).resolve().parent / "pages"
SPRITE = (Path(__file__).resolve().parent / "sprite.svg").read_text(encoding="utf-8").strip()

SITE_NAME = "Romantik Hotel Namenlos &amp; Fischerwiege"
TAGLINE = "Ostseebad Ahrenshoop"

NAV = [
    ("haeuser.html", "Häuser"),
    ("zimmer.html", "Zimmer &amp; Suiten"),
    ("kulinarik.html", "Kulinarik"),
    ("wellness.html", "Wellness"),
    ("arrangements.html", "Arrangements"),
    ("ahrenshoop.html", "Ahrenshoop"),
    ("kontakt.html", "Kontakt"),
]

BRAND = """<a class="brand" href="index.html">
          <svg class="brand__mark" aria-hidden="true" focusable="false"><use href="#i-signet"/></svg>
          <span class="brand__text">
            <span class="brand__name">Namenlos <span aria-hidden="true">&amp;</span> Fischerwiege</span>
            <span class="brand__sub">Romantik Hotel &middot; Ahrenshoop</span>
          </span>
        </a>"""


def nav_html(current):
    items = []
    for href, label in NAV:
        aria = ' aria-current="page"' if href == current else ""
        items.append('<li><a class="nav__link" href="{}"{}>{}</a></li>'.format(href, aria, label))
    return "\n              ".join(items)


def header_html(current, over_hero):
    cls = "header header--over-hero" if over_hero else "header"
    return """<header class="{cls}" id="siteHeader">
      <div class="header__inner">
        {brand}
        <nav class="nav" aria-label="Hauptnavigation">
          <div class="nav__panel" id="navPanel">
            <ul class="nav__list">
              {items}
            </ul>
            <span class="nav__cta"><a class="btn btn--sm" href="kontakt.html#anfrage">Anfragen</a></span>
          </div>
          <button class="theme-toggle" id="themeToggle" type="button"
                  aria-label="Zwischen hellem und dunklem Erscheinungsbild wechseln">
            <svg class="icon-sun" aria-hidden="true" focusable="false"><use href="#i-sun"/></svg>
            <svg class="icon-moon" aria-hidden="true" focusable="false"><use href="#i-moon"/></svg>
          </button>
          <button class="nav__toggle" id="navToggle" type="button"
                  aria-expanded="false" aria-controls="navPanel" aria-label="Menü öffnen">
            <span class="nav__toggle-bars" aria-hidden="true">
              <span class="nav__toggle-bar"></span>
              <span class="nav__toggle-bar"></span>
              <span class="nav__toggle-bar"></span>
            </span>
          </button>
        </nav>
      </div>
    </header>""".format(cls=cls, brand=BRAND, items=nav_html(current))


FOOTER = """<footer class="footer">
      <div class="container">
        <div class="footer__grid">
          <div class="footer__brand">
            <a class="brand" href="index.html">
              <svg class="brand__mark" aria-hidden="true" focusable="false"><use href="#i-signet"/></svg>
              <span class="brand__text">
                <span class="brand__name">Namenlos <span aria-hidden="true">&amp;</span> Fischerwiege</span>
                <span class="brand__sub">Romantik Hotel &middot; Ahrenshoop</span>
              </span>
            </a>
            <p>Vier reetgedeckte Häuser in den Dünen des Ostseebades Ahrenshoop,
               wenige Schritte vom Strand entfernt.</p>
          </div>
          <div>
            <h4>Aufenthalt</h4>
            <ul>
              <li><a href="haeuser.html">Die Häuser</a></li>
              <li><a href="zimmer.html">Zimmer &amp; Suiten</a></li>
              <li><a href="arrangements.html">Arrangements</a></li>
              <li><a href="wellness.html">Wellness</a></li>
            </ul>
          </div>
          <div>
            <h4>Genuss &amp; Umgebung</h4>
            <ul>
              <li><a href="kulinarik.html">Restaurant &amp; Seeterrasse</a></li>
              <li><a href="kulinarik.html#fruehstueck">Frühstück</a></li>
              <li><a href="ahrenshoop.html">Ahrenshoop entdecken</a></li>
              <li><a href="ahrenshoop.html#ausflug">Ausflüge</a></li>
            </ul>
          </div>
          <div>
            <h4>Kontakt</h4>
            <ul>
              <li>Dorfstraße 44<br>18347 Ostseebad Ahrenshoop</li>
              <li><a href="tel:+493822060600">+49&nbsp;38220&nbsp;606&nbsp;0</a></li>
              <li><a href="mailto:info@hotel-namenlos.de">info@hotel-namenlos.de</a></li>
              <li><a href="kontakt.html">Anreise &amp; Anfrage</a></li>
            </ul>
          </div>
        </div>
        <div class="footer__bottom">
          <span>&copy; <span id="year">2026</span> Romantik Hotel Namenlos &amp; Fischerwiege</span>
          <span class="footer__legal">
            <a href="impressum.html">Impressum</a>
            <a href="datenschutz.html">Datenschutz</a>
            <a href="kontakt.html">Kontakt</a>
          </span>
        </div>
      </div>
    </footer>"""

SHELL = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="theme-color" content="#0d2830">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="canonical" href="https://hotel-namenlos.de/{slug}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Romantik Hotel Namenlos &amp; Fischerwiege">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="assets/img/hero-duenen.svg">
<meta property="og:locale" content="de_DE">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&amp;family=Karla:wght@300;400;500;600;700&amp;display=swap">
<link rel="stylesheet" href="assets/css/style.css">
<script>
  // Applied before first paint so a chosen theme never flashes the other one.
  (function () {{
    try {{
      document.documentElement.classList.add('js');
      var t = localStorage.getItem('hn-theme');
      if (t === 'dark' || t === 'light') document.documentElement.dataset.theme = t;
    }} catch (e) {{}}
  }})();
</script>
{extra_head}</head>
<body>
    <a class="skip-link" href="#main">Zum Inhalt springen</a>
    {sprite}
    {header}
    <main id="main">
{body}
    </main>
    {footer}
    <script src="assets/js/main.js" defer></script>
</body>
</html>
"""


def parse(path):
    raw = path.read_text(encoding="utf-8")
    head, _, body = raw.partition("\n\n")
    meta = {}
    for line in head.strip().splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip()
    return meta, body.rstrip() + "\n"


def build():
    ROOT.mkdir(parents=True, exist_ok=True)
    built = []
    for src in sorted(PAGES.glob("*.html")):
        meta, body = parse(src)
        slug = src.name
        over_hero = meta.get("over_hero", "true").lower() == "true"
        html = SHELL.format(
            title=meta.get("title", SITE_NAME),
            description=meta.get("description", ""),
            slug="" if slug == "index.html" else slug,
            sprite=SPRITE,
            header=header_html(meta.get("nav", ""), over_hero),
            body=body,
            footer=FOOTER,
            extra_head=meta.get("extra_head", ""),
        )
        (ROOT / slug).write_text(html, encoding="utf-8")
        built.append((slug, len(html)))
    for slug, size in built:
        print("  {:<24} {:>7} bytes".format(slug, size))
    print("{} pages written to {}".format(len(built), ROOT))


if __name__ == "__main__":
    build()
