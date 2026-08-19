# Romantik Hotel Namenlos & Fischerwiege — Website

A static website for the hotel at
[hotel-namenlos.de](https://hotel-namenlos.de/), Dorfstraße 44, 18347 Ostseebad
Ahrenshoop. Ten pages in three languages — German, English, Ukrainian — with no
build dependencies, no JavaScript framework, and no external assets except two
Google Fonts families.

Open `index.html` in a browser and it works — from disk, from any static host,
from a CDN.

## Pages

| File | Contents |
| --- | --- |
| `index.html` | Home: hero, availability enquiry bar, the four houses, room categories, dining, wellness, Ahrenshoop |
| `haeuser.html` | The four houses of the ensemble and the facilities they share |
| `zimmer.html` | The four room categories, equipment tables, FAQ accordion |
| `kulinarik.html` | Restaurant, sea terrace, breakfast, the day's timeline |
| `wellness.html` | Both spa areas, practical information |
| `arrangements.html` | Four packaged stays, add-on services |
| `ahrenshoop.html` | The artists' colony, the cliff coast, excursions |
| `kontakt.html` | Enquiry form, contact details, how to get there |
| `impressum.html`, `datenschutz.html` | Legal pages — **contain placeholders, see below** |

Each page exists three times: German at the root, English under `en/`,
Ukrainian under `uk/`. Filenames stay the same in every language, so
`zimmer.html`, `en/zimmer.html` and `uk/zimmer.html` are the same page. Every
page carries `hreflang` alternates and a switcher in the header.

## Layout

```
index.html …                German pages   — generated, do not edit by hand
en/ …                       English pages  — generated
uk/ …                       Ukrainian pages — generated
robots.txt, sitemap.xml
assets/
  css/style.css             the whole design system, one file
  js/main.js                nav, theme toggle, reveals, accordion, date fields
  img/*.svg                 generated artwork
tools/
  build.py                  shell, navigation, footer and the language table
  bundle.py                 packs everything into one self-contained file
  make-art.py               draws every SVG in assets/img/
  sprite.svg                the icon set, inlined into each page
  pages/de|en|uk/*.html     the editable page bodies, one set per language
```

### Editing a page

Edit `tools/pages/<lang>/<name>.html`, then rebuild:

```bash
python3 tools/build.py
```

Each file there starts with a short front-matter block (`title`,
`description`, `nav`, `over_hero`, optional `extra_head`), a blank line, then
the markup that goes inside `<main>`. The header, footer, icon sprite and
`<head>` come from `tools/build.py` — change them there once and every page
picks it up.

### One-file preview build

`tools/bundle.py` packs the whole site into a single self-contained HTML file —
stylesheet and script inlined, all 23 SVGs embedded as data URIs, and all
thirty pages present as sections behind a small hash router (`#/de/zimmer`,
`#/en/kontakt/anfrage`). Useful for a preview link, an email attachment, or a
USB stick. Because every language shares one document, element ids are suffixed
per language (`anfrage--en`) so they cannot collide.

```bash
python3 tools/bundle.py             # dist/namenlos-vorschau.html  (~4.4 MB)
python3 tools/bundle.py --artifact  # same, without the html/head/body skeleton
```

The bundle carries a standing notice that it is a design draft and not the
hotel's official website. That notice exists only in the bundle — the
deployable pages in the repository root are unchanged.

### Editing the header, footer or navigation

All of it lives in `tools/build.py`. The `LANGS` table holds every string that
is not page content — navigation labels, footer headings, button text, the
skip link — one entry per language. `SHELL`, `header_html` and `footer_html`
build the chrome around them. Rebuild afterwards.

### Adding a language

Add an entry to `LANGS` in `tools/build.py`, add the language code to `ORDER`
and to `LANGS` in `tools/bundle.py`, then create `tools/pages/<code>/` with the
ten page bodies. Nothing else needs touching: the switcher, the `hreflang`
alternates and the sitemap follow from the table.

**A caveat worth knowing.** Page structure is duplicated per language rather
than driven by a message catalogue, because these pages are almost entirely
prose — a catalogue would hold whole paragraphs and buy little. The cost is
that a structural change to a page has to be made in each language's copy.

## The artwork

There is no photography here. Every image in `assets/img/` is a layered vector
scene drawn by `tools/make-art.py` from one palette — Bodden sea, dune sand,
reed gold — so the pictures belong to the same design as the type and colour.
Regenerate them with:

```bash
python3 tools/make-art.py
```

**Replacing them with real photographs is the expected next step.** The markup
uses plain `<img>` tags with explicit `width`/`height`, so dropping a JPEG in
place of an SVG under the same filename is all it takes. The sizes the layout
expects:

| Purpose | Files | Aspect |
| --- | --- | --- |
| Home hero | `hero-duenen.svg` | 16:9, wide crop |
| Page headers | `kopf-*.svg` | roughly 21:8 |
| Houses, rooms, dining, wellness, region | `haus-*`, `zimmer-*`, `kulinarik-*`, `wellness-*`, `ahrenshoop-*` | 4:3 |

## Design system

Everything is driven by custom properties at the top of `assets/css/style.css`:
a sea/sand/reed palette, a spacing scale, radii, shadows and two font stacks
(Cormorant Garamond for display, Karla for text). Light and dark are both
defined — dark follows the system setting and can be overridden by the toggle
in the header, which remembers the choice in `localStorage`.

## Accessibility and robustness

- Skip link, landmark elements, one `<h1>` per page, labelled form fields.
- The mobile menu, the accordion and the theme toggle are all keyboard
  operable and expose `aria-expanded`.
- Scroll reveals are suppressed under `prefers-reduced-motion`, are only armed
  when scripting is available (`html.js`), and are force-revealed on `load`, so
  content can never be left invisible.
- No horizontal overflow from 320 px upwards (verified at 320/390/768/1024).
- Decorative artwork carries `alt=""`; informative artwork is described.

## Before this goes live

1. **`impressum.html` and `datenschutz.html` contain `[…]` placeholders**, in
   all three languages. Company name, represented-by, register entry and VAT ID
   are legally required in Germany and were deliberately not invented. Fill them
   in and have all six pages reviewed. The English and Ukrainian versions each
   state that the German one is legally authoritative — confirm that this is how
   the operator wants it handled.
2. **No prices are published.** Every room and package says
   *„Preis auf Anfrage“* / *Price on request* / *Ціна за запитом*. Add rates
   once they are confirmed for the season.
3. **The enquiry form uses `mailto:`.** It opens the visitor's mail client and
   sends nothing by itself. For a real submission flow, point the `action` at a
   form endpoint on the host and remove the note beside the form.
4. **Google Fonts** are loaded from Google's CDN. To keep visitor IP addresses
   out of it, download both families into `assets/fonts/` and swap the
   `<link>` in `tools/build.py` for local `@font-face` rules.
5. **Facts to verify with the hotel:** phone extension, number of rooms per
   house, opening hours, spa times, whether dogs are accepted in which
   categories. The descriptive content was written from public directory
   listings, not from the hotel's own materials.
6. **Have the translations read by a native speaker.** The English and
   Ukrainian pages are translations of the German copy written here, not
   independently authored marketing text, and no one has proofread them against
   how the house actually talks about itself.

## Provenance of the content

The original site could not be retrieved while this was built — outbound
requests to `hotel-namenlos.de` were refused by the environment's egress proxy
(HTTP 403 on CONNECT), which also rules out downloading the hotel's own
photography from here. The factual points used here (address, telephone, four-star
rating, the ensemble of houses, roughly fifty units, ~50 m to the beach, the
two spa areas and what each contains, restaurant, sea terrace, breakfast
garden, café, underground parking, Romantik Hotels membership) come from public
directory and booking listings. Everything else — headings, descriptions,
package contents, FAQ answers — is newly written marketing copy and should be
checked against how the house actually operates before publication.
