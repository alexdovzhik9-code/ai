#!/usr/bin/env python3
"""
Bundles the whole site into one self-contained HTML file.

The built site is ten separate pages that link to each other and load their
CSS, JS and artwork from assets/. Some hosts — a preview link, an email
attachment, a USB stick — can only carry a single file. This packs everything
into one document: stylesheet and script inlined, every SVG embedded as a data
URI, all ten pages present as sections, and a small hash router (#/zimmer,
#/kontakt/anfrage) standing in for the links between them.

The output is a preview build, not the deployable site. It carries a standing
notice that it is a design draft rather than the hotel's official website.

Usage:  python3 tools/bundle.py [outfile]
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

ORDER = ["index", "haeuser", "zimmer", "kulinarik", "wellness",
         "arrangements", "ahrenshoop", "kontakt", "impressum", "datenschutz"]


def data_uri(svg_path):
    svg = svg_path.read_text(encoding="utf-8").strip()
    svg = re.sub(r"\s+", " ", svg)
    return "data:image/svg+xml," + quote(svg, safe="")


def rewrite_links(html, page):
    """Turn the inter-page links into hash routes, leaving SVG <use> alone."""
    def a_href(m):
        head, url, tail = m.group(1), m.group(2), m.group(3)
        if url.startswith(("http", "mailto:", "tel:", "data:")):
            return head + url + tail
        if url.startswith("#"):
            return head + "#/{}/{}".format(page, url[1:]) + tail
        target, _, frag = url.partition("#")
        if target.endswith(".html"):
            slug = target[:-5]
            route = "#/" + slug + ("/" + frag if frag else "")
            return head + route + tail
        return head + url + tail

    html = re.sub(r'(<a\b[^>]*?\shref=")([^"]+)(")', a_href, html)
    html = re.sub(r'(<form\b[^>]*?\saction=")([^"]+)(")', a_href, html)
    return html


def inline_images(html, images):
    def sub(m):
        head, url, tail = m.group(1), m.group(2), m.group(3)
        name = url.split("/")[-1]
        return head + images.get(name, url) + tail
    return re.sub(r'(<img\b[^>]*?\ssrc=")([^"]+)(")', sub, html)


def main():
    images = {p.name: data_uri(p) for p in sorted((ROOT / "assets" / "img").glob("*.svg"))}
    css = (ROOT / "assets" / "css" / "style.css").read_text(encoding="utf-8")
    js = (ROOT / "assets" / "js" / "main.js").read_text(encoding="utf-8")
    sprite = (ROOT / "tools" / "sprite.svg").read_text(encoding="utf-8").strip()

    # The header and footer are identical on every page; take them from one.
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    header = re.search(r'(<header class="header.*?</header>)', home, re.S).group(1)
    footer = re.search(r'(<footer class="footer">.*?</footer>)', home, re.S).group(1)
    header = re.sub(r'\sclass="header header--over-hero"', ' class="header"', header)
    header = re.sub(r'\saria-current="page"', "", header)
    header = rewrite_links(header, "index")
    footer = rewrite_links(footer, "index")

    sections = []
    for slug in ORDER:
        raw = (ROOT / slug + ".html").read_text(encoding="utf-8") if False else \
              (ROOT / (slug + ".html")).read_text(encoding="utf-8")
        body = re.search(r'<main id="main">(.*?)</main>', raw, re.S).group(1)
        title = re.search(r"<title>(.*?)</title>", raw, re.S).group(1).strip()
        over_hero = 'class="header header--over-hero"' in raw
        body = rewrite_links(body, slug)
        body = inline_images(body, images)
        sections.append(
            '<section class="route" id="route-{slug}" data-route="{slug}" '
            'data-hero="{hero}" data-title="{title}" hidden>{body}</section>'.format(
                slug=slug, hero="1" if over_hero else "0",
                title=title.replace('"', "&quot;"), body=body))

    router = """
/* ---------------------------------------------------------------- router
   The ten pages of the site live in this one file as .route sections.
   Links were rewritten to #/<page> and #/<page>/<anchor> when it was built. */
(function () {
  'use strict';
  var routes = document.querySelectorAll('.route');
  var header = document.getElementById('siteHeader');
  var links = document.querySelectorAll('.nav__link');
  var fallback = 'index';

  function parse() {
    var raw = (location.hash || '').replace(/^#\\/?/, '');
    var bits = raw.split('/').filter(Boolean);
    return { page: bits[0] || fallback, anchor: bits[1] || '' };
  }

  function show(page, anchor) {
    var found = false;
    Array.prototype.forEach.call(routes, function (s) {
      var match = s.dataset.route === page;
      s.hidden = !match;
      if (match) {
        found = true;
        document.title = s.dataset.title;
        header.classList.toggle('header--over-hero', s.dataset.hero === '1');
      }
    });
    if (!found) { show(fallback, ''); return; }

    Array.prototype.forEach.call(links, function (a) {
      var href = a.getAttribute('href') || '';
      if (href.indexOf('#/' + page) === 0) a.setAttribute('aria-current', 'page');
      else a.removeAttribute('aria-current');
    });

    // Re-run the reveal + form wiring for the section that just appeared.
    window.dispatchEvent(new Event('hn:route'));

    if (anchor) {
      var el = document.getElementById(anchor);
      if (el) { el.scrollIntoView({ block: 'start' }); return; }
    }
    window.scrollTo(0, 0);
  }

  function route() { var r = parse(); show(r.page, r.anchor); }
  window.addEventListener('hashchange', route);
  route();

  /* The hero search bar hands its values to the long enquiry form. */
  var quick = document.querySelector('#route-index form');
  if (quick) {
    quick.addEventListener('submit', function (e) {
      e.preventDefault();
      ['anreise', 'abreise', 'personen', 'haus'].forEach(function (key) {
        var from = quick.querySelector('[name="' + key + '"]');
        var to = document.querySelector('#anfrage [name="' + key + '"]');
        if (from && to && from.value) to.value = from.value;
      });
      location.hash = '#/kontakt/anfrage';
    });
  }
})();
"""

    # reveal observer needs to re-arm whenever a route becomes visible
    js = js.replace(
        "    window.addEventListener('load', function () {",
        "    var sweep = function () {")
    js = js.replace(
        """        if (box.top < window.innerHeight && box.bottom > 0) {
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

    banner_css = """
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
"""

    banner_html = """<aside class="preview-note" role="note">
      <strong>Designentwurf &mdash; nicht die offizielle Website des Hotels.</strong>
      <span>Vorschaubau ohne Preise; Impressum und Datenschutz enthalten Platzhalter.</span>
    </aside>"""

    doc = """<!DOCTYPE html>
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
/* Only the routed section is in the document flow. */
.route[hidden] {{ display: none; }}
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
    {header}
    <main id="main">
{sections}
    </main>
    {footer}
    {banner}
<script>
{js}
{router}
</script>
</body>
</html>
"""

    if ARTIFACT:
        # The Artifact host supplies <!doctype>, <html>, <head> and <body>.
        doc = doc[doc.index("<title>"):]
        doc = doc.replace("</head>\n<body>", "").replace("</body>\n</html>\n", "")

    html = doc.format(css=css, banner_css=banner_css, sprite=sprite, header=header,
                      sections="\n".join(sections), footer=footer, banner=banner_html,
                      js=js, router=router)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print("{}  {:.1f} KB  ({} pages, {} images inlined)".format(
        OUT, len(html.encode("utf-8")) / 1024, len(ORDER), len(images)))


if __name__ == "__main__":
    main()
