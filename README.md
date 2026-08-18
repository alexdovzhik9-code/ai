# ai

Workspace repository set up for UI work with Claude Code: the **UI/UX Pro Max**
design-intelligence skills (local, offline) and the **21st MCP** component
server (remote, needs an API key).

## Skills

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

## 21st MCP server

`.mcp.json` configures the [21st.dev](https://21st.dev/mcp) MCP server, which
searches the 21st component catalog and generates UI components. It complements
the skills above: the skills reason locally about style, color, and layout; the
MCP server fetches and generates actual component code.

**This needs your own API key before it will connect.** Get one at
<https://21st.dev/mcp>, then export it so Claude Code can expand it into the
`x-api-key` header:

```bash
export TWENTY_FIRST_API_KEY="your-key-here"
```

Put that in your shell profile (or a local `.envrc` — do not commit the key).
The config itself holds only the variable reference, so it is safe in version
control. Verify the connection with `claude mcp list` or `/mcp`; an unset
variable shows up there as a missing-variable warning.

### A note on `21st-dev/magic-mcp`

The old Magic MCP server (`@21st-dev/magic`) is deprecated. Upstream, that npm
package is now a thin stdio proxy that forwards to the same
`https://21st.dev/api/mcp` endpoint configured here, and all API keys issued by
the retired Magic console were reset. The direct HTTP config above is the
current, supported setup — one less process to spawn, and no `npx` on every
session start. The legacy tool names (`21st_magic_component_builder`,
`21st_magic_component_inspiration`, `21st_magic_component_refiner`,
`logo_search`) are still accepted and translated server-side; the current names
are `generate`, `get_inspiration`, `search`, `get_component`, and `search_logo`.

If you ever need the stdio proxy instead — for a client that cannot do HTTP MCP
— the equivalent entry is:

```json
{
  "mcpServers": {
    "21st": {
      "command": "npx",
      "args": ["-y", "@21st-dev/magic@latest"],
      "env": { "API_KEY_21ST": "${TWENTY_FIRST_API_KEY}" }
    }
  }
}
```

## Updating

The skill files are vendored, not fetched at runtime. To move to a newer
upstream release, replace `.claude/skills/` with the `.claude/skills/`
directory from the tagged release of the upstream repository, or run
`npx ui-ux-pro-max-cli init --ai claude --force` in this directory.

## Attribution

UI/UX Pro Max is © NextLevelBuilder and distributed under the MIT license.
The upstream license text is kept at `.claude/skills/LICENSE`.
Project home: <https://uupm.cc>
