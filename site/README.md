# Romantik Hotel Namenlos & Fischerwiege — Website

A static German-language website for the hotel at
[hotel-namenlos.de](https://hotel-namenlos.de/), Dorfstraße 44, 18347 Ostseebad
Ahrenshoop. Ten pages, no build dependencies, no JavaScript framework, no
external assets except two Google Fonts families.

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

## Layout

```
index.html …                generated pages — do not edit by hand
robots.txt, sitemap.xml
assets/
  css/style.css             the whole design system, one file
  js/main.js                nav, theme toggle, reveals, accordion, date fields
  img/*.svg                 generated artwork
tools/
  build.py                  wraps page bodies in the shared shell
  make-art.py               draws every SVG in assets/img/
  sprite.svg                the icon set, inlined into each page
  pages/*.html              the editable page bodies
```

### Editing a page

Edit `tools/pages/<name>.html`, then rebuild:

```bash
python3 tools/build.py
```

Each file there starts with a short front-matter block (`title`,
`description`, `nav`, `over_hero`, optional `extra_head`), a blank line, then
the markup that goes inside `<main>`. The header, footer, icon sprite and
`<head>` come from `tools/build.py` — change them there once and every page
picks it up.

### Editing the header, footer or navigation

All three live in `tools/build.py` (`NAV`, `BRAND`, `FOOTER`, `SHELL`). Rebuild
afterwards.

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

1. **`impressum.html` and `datenschutz.html` contain `[…]` placeholders.**
   Company name, represented-by, register entry and VAT ID are legally required
   in Germany and were deliberately not invented. Fill them in and have both
   pages reviewed.
2. **No prices are published.** Every room and package says
   *„Preis auf Anfrage“*. Add rates once they are confirmed for the season.
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

## Provenance of the content

The original site could not be retrieved while this was built — outbound
requests to `hotel-namenlos.de` were blocked by the network policy of the
environment. The factual points used here (address, telephone, four-star
rating, the ensemble of houses, roughly fifty units, ~50 m to the beach, the
two spa areas and what each contains, restaurant, sea terrace, breakfast
garden, café, underground parking, Romantik Hotels membership) come from public
directory and booking listings. Everything else — headings, descriptions,
package contents, FAQ answers — is newly written marketing copy and should be
checked against how the house actually operates before publication.
