#!/usr/bin/env python3
"""
Bundles the whole site — all three languages — into one self-contained HTML file.

The built site is thirty separate pages that link to each other and load their
CSS, JS and artwork from assets/. Some hosts — a preview link, an email
attachment, a USB stick — can only carry a single file. This packs everything
into one document: stylesheet and script inlined, every SVG embedded as a data
URI, all pages present as sections, and a small hash router
(#/de/zimmer, #/en/kontakt/anfrage) standing in for the links between them.

Because every language's pages live in the same document, their element ids
would collide. Each id is therefore suffixed with its language ("anfrage"
becomes "anfrage--en"), along with every reference to it.

The output is a preview build, not the deployable site. It carries a standing
notice that it is a design draft rather than the hotel's official website.

Usage:  python3 tools/bundle.py [outfile] [--artifact]
"""

import re
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
ARTIFACT = "--artifact" in sys.argv
OUT = Path(ARGS[0]) if ARGS else (
    ROOT / "dist" / ("namenlos-artifact.html" if ARTIFACT else "namenlos-vorschau.html"))

LANGS = ["de", "en", "uk"]
DIRS = {"de": "", "en": "en", "uk": "uk"}
SLUGS = ["index", "haeuser", "zimmer", "kulinarik", "wellness",
         "arrangements", "ahrenshoop", "kontakt", "impressum", "datenschutz"]

NOTE = {
    "de": ("Designentwurf &mdash; nicht die offizielle Website des Hotels.",
           "Vorschaubau ohne Preise; Impressum und Datenschutz enthalten Platzhalter."),
    "en": ("Design draft &mdash; not the hotel's official website.",
           "Preview build without prices; the legal pages contain placeholders."),
    "uk": ("Дизайн-макет &mdash; не офіційний сайт готелю.",
           "Демоверсія без цін; правові сторінки містять заповнювачі."),
}


def data_uri(svg_path):
    svg = re.sub(r"\s+", " ", svg_path.read_text(encoding="utf-8").strip())
    return "data:image/svg+xml," + quote(svg, safe="")


def suffix_ids(html, lang):
    """Make every id in this language's markup unique, references included."""
    ids = set(re.findall(r'\sid="([^"]+)"', html))
    if not ids:
        return html
    alt = "|".join(re.escape(i) for i in sorted(ids, key=len, reverse=True))
    for attr in ("id", "for", "aria-controls", "aria-labelledby"):
        html = re.sub(r'(\s%s=")(%s)(")' % (attr, alt),
                      lambda m: m.group(1) + m.group(2) + "--" + lang + m.group(3), html)
    # in-page anchors written as href="#thing"
    html = re.sub(r'(<a\b[^>]*?\shref="#)(%s)(")' % alt,
                  lambda m: m.group(1) + m.group(2) + "--" + lang + m.group(3), html)
    return html


def rewrite_links(html, lang, page):
    """Turn every link into a hash route, leaving SVG <use> and protocols alone."""
    def target(url):
        if url.startswith(("http", "mailto:", "tel:", "data:")):
            return url
        if url.startswith("#"):
            return "#/{}/{}/{}".format(lang, page, url[1:])
        path, _, frag = url.partition("#")
        # a language switch: "en/zimmer.html", "../zimmer.html", "../uk/zimmer.html"
        bits = [b for b in path.split("/") if b not in ("", "..")]
        dest_lang = lang
        if bits and bits[0] in ("en", "uk"):
            dest_lang, bits = bits[0], bits[1:]
        elif path.startswith("../") and len(bits) == 1:
            dest_lang = "de"
        if not bits or not bits[0].endswith(".html"):
            return url
        slug = bits[0][:-5]
        return "#/{}/{}{}".format(dest_lang, slug, "/" + frag if frag else "")

    def sub(m):
        return m.group(1) + target(m.group(2)) + m.group(3)

    html = re.sub(r'(<a\b[^>]*?\shref=")([^"]+)(")', sub, html)
    html = re.sub(r'(<form\b[^>]*?\saction=")([^"]+)(")', sub, html)
    return html


def inline_images(html, images):
    def sub(m):
        return m.group(1) + images.get(m.group(2).split("/")[-1], m.group(2)) + m.group(3)
    return re.sub(r'(<img\b[^>]*?\ssrc=")([^"]+)(")', sub, html)


ROUTER = """
/* ---------------------------------------------------------------- router
   Thirty pages live in this one file as .route sections, three languages
   deep. Links were rewritten to #/<lang>/<page> and #/<lang>/<page>/<anchor>
   when it was built; element ids carry a "--<lang>" suffix. */
(function () {
  'use strict';
  var routes = document.querySelectorAll('.route');
  var shells = document.querySelectorAll('.shell');
  var skip = document.querySelector('.skip-link');
  var fallback = { lang: 'de', page: 'index' };

  function parse() {
    var bits = (location.hash || '').replace(/^#\\/?/, '').split('/').filter(Boolean);
    var lang = ['de', 'en', 'uk'].indexOf(bits[0]) > -1 ? bits[0] : fallback.lang;
    var offset = lang === bits[0] ? 1 : 0;
    return { lang: lang, page: bits[offset] || fallback.page, anchor: bits[offset + 1] || '' };
  }

  function show(lang, page, anchor) {
    var active = null;
    Array.prototype.forEach.call(routes, function (s) {
      var match = s.dataset.lang === lang && s.dataset.route === page;
      s.hidden = !match;
      if (match) active = s;
    });
    if (!active) { show(fallback.lang, fallback.page, ''); return; }

    document.title = active.dataset.title;
    document.documentElement.lang = lang;

    Array.prototype.forEach.call(shells, function (sh) {
      var mine = sh.dataset.lang === lang;
      sh.hidden = !mine;
      if (!mine) return;
      sh.querySelector('#siteHeader')
        .classList.toggle('header--over-hero', active.dataset.hero === '1');
      Array.prototype.forEach.call(sh.querySelectorAll('.nav__link'), function (a) {
        var href = a.getAttribute('href') || '';
        if (href === '#/' + lang + '/' + page) a.setAttribute('aria-current', 'page');
        else a.removeAttribute('aria-current');
      });
    });
    if (skip) skip.setAttribute('href', '#main');

    window.dispatchEvent(new Event('hn:route'));

    if (anchor) {
      var el = document.getElementById(anchor + '--' + lang) || document.getElementById(anchor);
      if (el) { el.scrollIntoView({ block: 'start' }); return; }
    }
    window.scrollTo(0, 0);
  }

  function route() { var r = parse(); show(r.lang, r.page, r.anchor); }
  window.addEventListener('hashchange', route);
  route();

  /* The hero search bar hands its values to that language's enquiry form. */
  Array.prototype.forEach.call(
    document.querySelectorAll('.route[data-route="index"] form'), function (quick) {
      var lang = quick.closest('.route').dataset.lang;
      quick.addEventListener('submit', function (e) {
        e.preventDefault();
        ['anreise', 'abreise', 'personen', 'haus'].forEach(function (key) {
          var from = quick.querySelector('[name="' + key + '"]');
          var to = document.querySelector(
            '.route[data-lang="' + lang + '"][data-route="kontakt"] [name="' + key + '"]');
          if (from && to && from.value) to.value = from.value;
        });
        location.hash = '#/' + lang + '/kontakt/anfrage';
      });
    });
})();
"""

BANNER_CSS = """
/* ------------------------------------------------- preview-build notice */
body { padding-bottom: 3.25rem; }
.preview-note {
  position: fixed;
  inset: auto 0 0 0;
  z-index: 300;
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: center;
  gap: .35rem 1rem;
  padding: .7rem 1.25rem;
  background: var(--sea-900);
  color: rgba(253, 250, 245, .72);
  border-top: 2px solid var(--accent);
  font-size: .8rem;
  line-height: 1.45;
  text-align: center;
}
.preview-note strong { color: var(--sand-50); font-weight: 600; }
.preview-note span { color: rgba(253, 250, 245, .5); }
@media (max-width: 620px) {
  body { padding-bottom: 4.5rem; }
  .preview-note { font-size: .74rem; }
}
@media print { .preview-note { display: none; } body { padding-bottom: 0; } }
.route[hidden], .shell[hidden], .preview-note[hidden] { display: none; }
"""

DOC = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Namenlos &amp; Fischerwiege</title>
<meta name="description" content="Designentwurf für das Romantik Hotel Namenlos &amp; Fischerwiege im Ostseebad Ahrenshoop.">
<meta name="theme-color" content="#0d2830">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&amp;family=Karla:wght@300;400;500;600;700&amp;display=swap">
<style>
{css}
{banner_css}
</style>
<script>
  (function () {{
    try {{
      document.documentElement.classList.add('js');
      var t = localStorage.getItem('hn-theme');
      if (t === 'dark' || t === 'light') document.documentElement.dataset.theme = t;
    }} catch (e) {{}}
  }})();
</script>
</head>
<body>
    <a class="skip-link" href="#main">Zum Inhalt springen</a>
    {sprite}
{headers}
    <main id="main">
{sections}
    </main>
{footers}
{banners}
<script>
{js}
{router}
</script>
</body>
</html>
"""


def main():
    images = {p.name: data_uri(p) for p in sorted((ROOT / "assets" / "img").glob("*.svg"))}
    css = (ROOT / "assets" / "css" / "style.css").read_text(encoding="utf-8")
    js = (ROOT / "assets" / "js" / "main.js").read_text(encoding="utf-8")
    sprite = (ROOT / "tools" / "sprite.svg").read_text(encoding="utf-8").strip()

    # the reveal sweep has to run again whenever a route becomes visible
    js = js.replace("    window.addEventListener('load', function () {", "    var sweep = function () {")
    js = js.replace("""        if (box.top < window.innerHeight && box.bottom > 0) {
          el.classList.add('is-visible');
          observer.unobserve(el);
        }
      });
    });""",
        """        if (box.top < window.innerHeight && box.bottom > 0) {
          el.classList.add('is-visible');
          observer.unobserve(el);
        }
      });
    };
    window.addEventListener('load', sweep);
    window.addEventListener('hn:route', function () { setTimeout(sweep, 0); });""")

    headers, footers, sections, banners = [], [], [], []
    for lang in LANGS:
        d = ROOT / DIRS[lang] if DIRS[lang] else ROOT
        home = (d / "index.html").read_text(encoding="utf-8")
        head = re.search(r'(<header class="header.*?</header>)', home, re.S).group(1)
        foot = re.search(r'(<footer class="footer">.*?</footer>)', home, re.S).group(1)
        head = head.replace(' class="header header--over-hero"', ' class="header"')
        head = re.sub(r'\said="siteHeader"', ' id="siteHeader"', head)
        head = re.sub(r'\saria-current="page"', "", head)
        head = suffix_ids(head, lang)
        head = rewrite_links(head, lang, "index")
        foot = suffix_ids(foot, lang)
        foot = rewrite_links(foot, lang, "index")
        headers.append('<div class="shell" data-lang="{}" hidden>{}</div>'.format(lang, head))
        footers.append('<div class="shell" data-lang="{}" hidden>{}</div>'.format(lang, foot))
        strong, small = NOTE[lang]
        banners.append(
            '<aside class="shell preview-note" data-lang="{}" role="note" hidden>'
            '<strong>{}</strong> <span>{}</span></aside>'.format(lang, strong, small))

        for slug in SLUGS:
            raw = (d / (slug + ".html")).read_text(encoding="utf-8")
            body = re.search(r'<main id="main">(.*?)</main>', raw, re.S).group(1)
            title = re.search(r"<title>(.*?)</title>", raw, re.S).group(1).strip()
            over = 'class="header header--over-hero"' in raw
            body = suffix_ids(body, lang)
            body = rewrite_links(body, lang, slug)
            body = inline_images(body, images)
            sections.append(
                '<section class="route" data-lang="{lang}" data-route="{slug}" '
                'data-hero="{hero}" data-title="{title}" hidden>{body}</section>'.format(
                    lang=lang, slug=slug, hero="1" if over else "0",
                    title=title.replace('"', "&quot;"), body=body))

    doc = DOC
    if ARTIFACT:
        # The Artifact host supplies <!doctype>, <html>, <head> and <body>.
        doc = doc[doc.index("<title>"):]
        doc = doc.replace("</head>\n<body>", "").replace("</body>\n</html>\n", "")

    html = doc.format(css=css, banner_css=BANNER_CSS, sprite=sprite,
                      headers="\n".join(headers), sections="\n".join(sections),
                      footers="\n".join(footers), banners="\n".join(banners),
                      js=js, router=ROUTER)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print("{}  {:.1f} KB  ({} pages, {} languages, {} images inlined)".format(
        OUT, len(html.encode("utf-8")) / 1024, len(SLUGS) * len(LANGS), len(LANGS), len(images)))


if __name__ == "__main__":
    main()
