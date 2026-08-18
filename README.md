# ai

Workspace repository with the **UI/UX Pro Max** design-intelligence skill set installed for Claude Code.

## What's installed

`.claude/skills/` contains the seven skills that ship with
[nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
v2.13.0 — the same layout `uipro init --ai claude` produces:

| Skill | Purpose |
| --- | --- |
| `ui-ux-pro-max` | Orchestrator. Searchable database of UI styles, color palettes, font pairings, UX guidelines, icons, charts, and per-stack implementation notes. |
| `design` | Brand identity, logos, corporate identity program, presentations, banners, icons, social images. |
| `design-system` | Three-layer token architecture (primitive → semantic → component), component specs, slide generation. |
| `ui-styling` | shadcn/ui + Tailwind component and layout patterns. |
| `brand` | Brand voice, messaging frameworks, asset management, consistency checks. |
| `slides` | Strategic HTML presentations with Chart.js. |
| `banner-design` | Social, ad, web-hero, and print banner formats. |

## Usage

The skills auto-activate on UI/UX requests — just describe what you want:

```
Build a landing page for my SaaS product
Create a dashboard for healthcare analytics
Design a portfolio website with dark mode
```

You can also query the local database directly. Python 3 is the only
requirement; the scripts use the standard library and make no network calls.

```bash
# Domain search: product, style, typography, color, landing, chart, ux,
#                icons, react, web, google-fonts, gsap
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "saas landing page" --domain style -n 5

# Stack-specific guidance
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "form validation" --stack nextjs

# Generate a full design system (pattern, style, colors, typography, checklist)
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "beauty spa landing page" --design-system
```

Optional dials for `--design-system`: `--variance 1-10` (centered/minimal →
bold/asymmetric), `--motion 1-10` (attaches a matching GSAP snippet),
`--density 1-10` (spacious → dashboard-dense).

## Updating

The skill files are vendored, not fetched at runtime. To move to a newer
upstream release, replace `.claude/skills/` with the `.claude/skills/`
directory from the tagged release of the upstream repository, or run
`npx ui-ux-pro-max-cli init --ai claude --force` in this directory.

## Attribution

UI/UX Pro Max is © NextLevelBuilder and distributed under the MIT license.
The upstream license text is kept at `.claude/skills/LICENSE`.
Project home: <https://uupm.cc>
