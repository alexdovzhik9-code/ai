#!/usr/bin/env python3
"""
Assembles the static pages, in every language.

Each file in tools/pages/<lang>/<slug>.html holds only the page body: a
front-matter block of `key: value` lines, a blank line, then the markup that
goes inside <main>. This script wraps that in the shared shell (head, icon
sprite, header, footer) and writes the page to the site root for German, and
into en/ and uk/ for the other two.

German is the primary language and lives at the root; the others sit one
directory down, so their asset and cross-links carry a "../" prefix.

Run after editing any page or the shell:  python3 tools/build.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = Path(__file__).resolve().parent / "pages"
SPRITE = (Path(__file__).resolve().parent / "sprite.svg").read_text(encoding="utf-8").strip()

SITE_URL = "https://hotel-namenlos.de/"

SLUGS = ["index", "haeuser", "zimmer", "kulinarik", "wellness",
         "arrangements", "ahrenshoop", "kontakt", "impressum", "datenschutz"]

# ---------------------------------------------------------------- languages
LANGS = {
    "de": {
        "code": "de", "hreflang": "de", "dir": "", "label": "Deutsch", "short": "DE",
        "locale": "de_DE",
        "skip": "Zum Inhalt springen",
        "nav_label": "Hauptnavigation",
        "menu_open": "Menü öffnen",
        "theme": "Zwischen hellem und dunklem Erscheinungsbild wechseln",
        "lang_label": "Sprache wählen",
        "cta": "Anfragen",
        "cta_href": "kontakt.html#anfrage",
        "brand_sub": "Romantik Hotel &middot; Ahrenshoop",
        "nav": [("haeuser.html", "Häuser"), ("zimmer.html", "Zimmer &amp; Suiten"),
                ("kulinarik.html", "Kulinarik"), ("wellness.html", "Wellness"),
                ("arrangements.html", "Arrangements"), ("ahrenshoop.html", "Ahrenshoop"),
                ("kontakt.html", "Kontakt")],
        "foot_blurb": ("Vier reetgedeckte Häuser in den Dünen des Ostseebades Ahrenshoop, "
                       "wenige Schritte vom Strand entfernt."),
        "foot_stay": "Aufenthalt",
        "foot_stay_links": [("haeuser.html", "Die Häuser"), ("zimmer.html", "Zimmer &amp; Suiten"),
                            ("arrangements.html", "Arrangements"), ("wellness.html", "Wellness")],
        "foot_taste": "Genuss &amp; Umgebung",
        "foot_taste_links": [("kulinarik.html", "Restaurant &amp; Seeterrasse"),
                             ("kulinarik.html#fruehstueck", "Frühstück"),
                             ("ahrenshoop.html", "Ahrenshoop entdecken"),
                             ("ahrenshoop.html#ausflug", "Ausflüge")],
        "foot_contact": "Kontakt",
        "foot_contact_link": ("kontakt.html", "Anreise &amp; Anfrage"),
        "foot_legal": [("impressum.html", "Impressum"), ("datenschutz.html", "Datenschutz"),
                       ("kontakt.html", "Kontakt")],
    },
    "en": {
        "code": "en", "hreflang": "en", "dir": "en", "label": "English", "short": "EN",
        "locale": "en_GB",
        "skip": "Skip to content",
        "nav_label": "Main navigation",
        "menu_open": "Open menu",
        "theme": "Switch between light and dark appearance",
        "lang_label": "Choose language",
        "cta": "Enquire",
        "cta_href": "kontakt.html#anfrage",
        "brand_sub": "Romantik Hotel &middot; Ahrenshoop",
        "nav": [("haeuser.html", "Houses"), ("zimmer.html", "Rooms &amp; Suites"),
                ("kulinarik.html", "Dining"), ("wellness.html", "Spa"),
                ("arrangements.html", "Packages"), ("ahrenshoop.html", "Ahrenshoop"),
                ("kontakt.html", "Contact")],
        "foot_blurb": ("Four thatched houses in the dunes of the Baltic resort of "
                       "Ahrenshoop, a few steps from the beach."),
        "foot_stay": "Your stay",
        "foot_stay_links": [("haeuser.html", "The houses"), ("zimmer.html", "Rooms &amp; suites"),
                            ("arrangements.html", "Packages"), ("wellness.html", "Spa")],
        "foot_taste": "Table &amp; surroundings",
        "foot_taste_links": [("kulinarik.html", "Restaurant &amp; sea terrace"),
                             ("kulinarik.html#fruehstueck", "Breakfast"),
                             ("ahrenshoop.html", "Discover Ahrenshoop"),
                             ("ahrenshoop.html#ausflug", "Day trips")],
        "foot_contact": "Contact",
        "foot_contact_link": ("kontakt.html", "Directions &amp; enquiry"),
        "foot_legal": [("impressum.html", "Legal notice"), ("datenschutz.html", "Privacy"),
                       ("kontakt.html", "Contact")],
    },
    "uk": {
        "code": "uk", "hreflang": "uk", "dir": "uk", "label": "Українська", "short": "UA",
        "locale": "uk_UA",
        "skip": "Перейти до вмісту",
        "nav_label": "Головна навігація",
        "menu_open": "Відкрити меню",
        "theme": "Перемкнути світле й темне оформлення",
        "lang_label": "Обрати мову",
        "cta": "Запит",
        "cta_href": "kontakt.html#anfrage",
        "brand_sub": "Romantik Hotel &middot; Аренсгоп",
        "nav": [("haeuser.html", "Будинки"), ("zimmer.html", "Номери"),
                ("kulinarik.html", "Кухня"), ("wellness.html", "Велнес"),
                ("arrangements.html", "Пропозиції"), ("ahrenshoop.html", "Аренсгоп"),
                ("kontakt.html", "Контакти")],
        "foot_blurb": ("Чотири будинки під очеретяними дахами в дюнах балтійського "
                       "курорту Аренсгоп, за кілька кроків від пляжу."),
        "foot_stay": "Перебування",
        "foot_stay_links": [("haeuser.html", "Будинки"), ("zimmer.html", "Номери та люкси"),
                            ("arrangements.html", "Пропозиції"), ("wellness.html", "Велнес")],
        "foot_taste": "Смак і околиці",
        "foot_taste_links": [("kulinarik.html", "Ресторан і тераса"),
                             ("kulinarik.html#fruehstueck", "Сніданок"),
                             ("ahrenshoop.html", "Відкрити Аренсгоп"),
                             ("ahrenshoop.html#ausflug", "Поїздки")],
        "foot_contact": "Контакти",
        "foot_contact_link": ("kontakt.html", "Як дістатися та запит"),
        "foot_legal": [("impressum.html", "Вихідні дані"), ("datenschutz.html", "Приватність"),
                       ("kontakt.html", "Контакти")],
    },
}

ORDER = ["de", "en", "uk"]


def brand(L, base):
    return """<a class="brand" href="{base}index.html">
          <svg class="brand__mark" aria-hidden="true" focusable="false"><use href="#i-signet"/></svg>
          <span class="brand__text">
            <span class="brand__name">Namenlos <span aria-hidden="true">&amp;</span> Fischerwiege</span>
            <span class="brand__sub">{sub}</span>
          </span>
        </a>""".format(base=base, sub=L["brand_sub"])


def lang_switch(current, slug):
    """Links to the same page in the other languages."""
    items = []
    for code in ORDER:
        other = LANGS[code]
        if code == current["code"]:
            items.append('<li><span class="lang__item lang__item--on" aria-current="true">'
                         '{}</span></li>'.format(other["short"]))
            continue
        # from de/ (root) to en/ ; from en/ to root or ../uk/
        if current["dir"] == "":
            href = ("{}/{}.html".format(other["dir"], slug)) if other["dir"] else slug + ".html"
        else:
            href = ("../{}.html".format(slug) if not other["dir"]
                    else "../{}/{}.html".format(other["dir"], slug))
        items.append('<li><a class="lang__item" href="{}" hreflang="{}" lang="{}" '
                     'title="{}">{}</a></li>'.format(href, other["hreflang"], other["hreflang"],
                                                     other["label"], other["short"]))
    return ('<ul class="lang" aria-label="{}">\n              {}\n            </ul>'
            .format(current["lang_label"], "\n              ".join(items)))


def nav_html(L, current_page):
    items = []
    for href, label in L["nav"]:
        aria = ' aria-current="page"' if href == current_page else ""
        items.append('<li><a class="nav__link" href="{}"{}>{}</a></li>'.format(href, aria, label))
    return "\n              ".join(items)


def header_html(L, base, slug, current_page, over_hero):
    cls = "header header--over-hero" if over_hero else "header"
    return """<header class="{cls}" id="siteHeader">
      <div class="header__inner">
        {brand}
        <nav class="nav" aria-label="{navlabel}">
          <div class="nav__panel" id="navPanel">
            <ul class="nav__list">
              {items}
            </ul>
            {lang}
            <span class="nav__cta"><a class="btn btn--sm" href="{ctahref}">{cta}</a></span>
          </div>
          <button class="theme-toggle" id="themeToggle" type="button" aria-label="{theme}">
            <svg class="icon-sun" aria-hidden="true" focusable="false"><use href="#i-sun"/></svg>
            <svg class="icon-moon" aria-hidden="true" focusable="false"><use href="#i-moon"/></svg>
          </button>
          <button class="nav__toggle" id="navToggle" type="button"
                  aria-expanded="false" aria-controls="navPanel" aria-label="{menu}">
            <span class="nav__toggle-bars" aria-hidden="true">
              <span class="nav__toggle-bar"></span>
              <span class="nav__toggle-bar"></span>
              <span class="nav__toggle-bar"></span>
            </span>
          </button>
        </nav>
      </div>
    </header>""".format(cls=cls, brand=brand(L, base), navlabel=L["nav_label"],
                        items=nav_html(L, current_page), lang=lang_switch(L, slug),
                        ctahref=L["cta_href"], cta=L["cta"], theme=L["theme"],
                        menu=L["menu_open"])


def links(pairs):
    return "\n              ".join('<li><a href="{}">{}</a></li>'.format(h, t) for h, t in pairs)


def footer_html(L, base):
    return """<footer class="footer">
      <div class="container">
        <div class="footer__grid">
          <div class="footer__brand">
            {brand}
            <p>{blurb}</p>
          </div>
          <div>
            <h4>{stay}</h4>
            <ul>
              {stay_links}
            </ul>
          </div>
          <div>
            <h4>{taste}</h4>
            <ul>
              {taste_links}
            </ul>
          </div>
          <div>
            <h4>{contact}</h4>
            <ul>
              <li>Dorfstraße 44<br>18347 Ostseebad Ahrenshoop</li>
              <li><a href="tel:+493822060600">+49&nbsp;38220&nbsp;606&nbsp;0</a></li>
              <li><a href="mailto:info@hotel-namenlos.de">info@hotel-namenlos.de</a></li>
              {contact_link}
            </ul>
          </div>
        </div>
        <div class="footer__bottom">
          <span>&copy; <span id="year">2026</span> Romantik Hotel Namenlos &amp; Fischerwiege</span>
          <span class="footer__legal">
            {legal}
          </span>
        </div>
      </div>
    </footer>""".format(
        brand=brand(L, base), blurb=L["foot_blurb"], stay=L["foot_stay"],
        stay_links=links(L["foot_stay_links"]), taste=L["foot_taste"],
        taste_links=links(L["foot_taste_links"]), contact=L["foot_contact"],
        contact_link='<li><a href="{}">{}</a></li>'.format(*L["foot_contact_link"]),
        legal="\n            ".join('<a href="{}">{}</a>'.format(h, t) for h, t in L["foot_legal"]))


def alternates(slug):
    out = []
    for code in ORDER:
        other = LANGS[code]
        loc = SITE_URL + (other["dir"] + "/" if other["dir"] else "")
        loc += "" if slug == "index" else slug + ".html"
        out.append('<link rel="alternate" hreflang="{}" href="{}">'.format(other["hreflang"], loc))
    out.append('<link rel="alternate" hreflang="x-default" href="{}{}">'.format(
        SITE_URL, "" if slug == "index" else slug + ".html"))
    return "\n".join(out)


SHELL = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="theme-color" content="#0d2830">
<link rel="icon" href="{base}assets/img/favicon.svg" type="image/svg+xml">
<link rel="canonical" href="{canonical}">
{alternates}
<meta property="og:type" content="website">
<meta property="og:site_name" content="Romantik Hotel Namenlos &amp; Fischerwiege">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{base}assets/img/hero-duenen.svg">
<meta property="og:locale" content="{locale}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&amp;family=Karla:wght@300;400;500;600;700&amp;display=swap">
<link rel="stylesheet" href="{base}assets/css/style.css">
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
    <a class="skip-link" href="#main">{skip}</a>
    {sprite}
    {header}
    <main id="main">
{body}
    </main>
    {footer}
    <script src="{base}assets/js/main.js" defer></script>
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


PRIORITY = {"index": "1.0", "haeuser": "0.9", "zimmer": "0.9", "kontakt": "0.9",
            "kulinarik": "0.8", "wellness": "0.8", "arrangements": "0.8",
            "ahrenshoop": "0.7", "impressum": "0.2", "datenschutz": "0.2"}


def write_sitemap():
    """One entry per page per language, each listing its alternates."""
    import datetime
    today = datetime.date.today().isoformat()
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
           '        xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for code in ORDER:
        L = LANGS[code]
        for slug in SLUGS:
            loc = SITE_URL + (L["dir"] + "/" if L["dir"] else "")
            loc += "" if slug == "index" else slug + ".html"
            out.append("  <url>")
            out.append("    <loc>{}</loc>".format(loc))
            for other_code in ORDER:
                o = LANGS[other_code]
                alt = SITE_URL + (o["dir"] + "/" if o["dir"] else "")
                alt += "" if slug == "index" else slug + ".html"
                out.append('    <xhtml:link rel="alternate" hreflang="{}" href="{}"/>'.format(
                    o["hreflang"], alt))
            out.append("    <lastmod>{}</lastmod>".format(today))
            out.append("    <priority>{}</priority>".format(PRIORITY.get(slug, "0.5")))
            out.append("  </url>")
    out.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(out) + "\n", encoding="utf-8")
    return len(ORDER) * len(SLUGS)


def build():
    built = []
    for code in ORDER:
        L = LANGS[code]
        outdir = ROOT / L["dir"] if L["dir"] else ROOT
        outdir.mkdir(parents=True, exist_ok=True)
        base = "../" if L["dir"] else ""
        src_dir = PAGES / code
        for slug in SLUGS:
            src = src_dir / (slug + ".html")
            if not src.exists():
                print("  !! missing {}/{}".format(code, src.name))
                continue
            meta, body = parse(src)
            over_hero = meta.get("over_hero", "true").lower() == "true"
            canonical = SITE_URL + (L["dir"] + "/" if L["dir"] else "")
            canonical += "" if slug == "index" else slug + ".html"
            html = SHELL.format(
                lang=L["code"],
                title=meta.get("title", "Romantik Hotel Namenlos & Fischerwiege"),
                description=meta.get("description", ""),
                canonical=canonical,
                alternates=alternates(slug),
                locale=L["locale"],
                base=base,
                sprite=SPRITE,
                header=header_html(L, base, slug, meta.get("nav", ""), over_hero),
                body=body,
                footer=footer_html(L, base),
                skip=L["skip"],
                extra_head=meta.get("extra_head", ""),
            )
            (outdir / (slug + ".html")).write_text(html, encoding="utf-8")
            built.append("{}/{}".format(code, slug))
    n = write_sitemap()
    print("{} pages written ({} languages), sitemap.xml with {} urls".format(
        len(built), len(ORDER), n))
    for code in ORDER:
        n = len([b for b in built if b.startswith(code + "/")])
        print("  {}  {} pages".format(LANGS[code]["short"], n))


if __name__ == "__main__":
    build()
