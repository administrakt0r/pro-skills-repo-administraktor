# README Design Styles — Full Templates

Read only the section for the design the user picked, unless you're helping them decide between designs (in which case skim all four headers + "best for" lines).

Every template below uses real Markdown that renders correctly on GitHub. Replace every `{{bracketed}}` placeholder. Do not leave a placeholder unfilled and unmarked — if info is missing, write an obvious inline note like `<!-- TODO: add real demo GIF -->` rather than inventing a fake value.

---

## 1. Minimal & Badge-Driven

**Best for:** CLI tools, infra/dev-tooling libraries, mature serious packages, anything targeting experienced developers who want to scan fast and not be marketed at.

**Tone:** Terse, confident, zero fluff. No emoji in headers. Let the badges and code speak.

```markdown
<div align="center">

# {{Project Name}}

{{One-sentence description, keyword-forward}}

[![License](https://img.shields.io/github/license/{{owner}}/{{repo}})](LICENSE)
[![Build](https://img.shields.io/github/actions/workflow/status/{{owner}}/{{repo}}/{{workflow}}.yml)]({{ci_url}})
[![Version](https://img.shields.io/{{registry}}/v/{{package}})]({{package_url}})
[![Downloads](https://img.shields.io/{{registry}}/dm/{{package}})]({{package_url}})

</div>

## Table of Contents

- [Installation](#installation)
- [Quickstart](#quickstart)
- [Usage](#usage)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

## Installation

\`\`\`bash
{{install command}}
\`\`\`

Requires {{runtime + version, e.g. "Node.js 18+"}}.

## Quickstart

\`\`\`{{lang}}
{{smallest possible working example}}
\`\`\`

## Usage

{{expanded examples / common patterns}}

## Configuration

{{options table if applicable}}

## API Reference

{{link to full docs, or inline if small}}

## Contributing

Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) {{or short inline guide}}.

## License

[{{License name}}](LICENSE)
```

---

## 2. Visual Hero / Landing Page

**Best for:** apps with a UI, browser/VS Code extensions, anything visual, projects trying to win attention fast on GitHub trending/Twitter.

**Tone:** Warm, energetic, show-don't-tell. Emoji used sparingly as visual anchors in section headers, not decoration everywhere.

```markdown
<div align="center">
  <img src="{{logo or banner path}}" alt="{{Project Name}} logo" width="{{e.g. 120}}" />

  # {{Project Name}}

  ### {{punchy one-line tagline}}

  {{one or two sentences: what it does, who it's for}}

  [![License](https://img.shields.io/github/license/{{owner}}/{{repo}})](LICENSE)
  [![Stars](https://img.shields.io/github/stars/{{owner}}/{{repo}}?style=social)]({{repo_url}})
  [![Version](https://img.shields.io/{{registry}}/v/{{package}})]({{package_url}})

  [**Demo**]({{demo_url}}) · [**Docs**]({{docs_url}}) · [**Report a bug**]({{issues_url}})

</div>

<p align="center">
  <img src="{{screenshot or gif path}}" alt="{{Project Name}} demo showing {{what's happening}}" width="720" />
</p>

## Table of Contents

- [Features](#features)
- [Quickstart](#quickstart)
- [Installation](#installation)
- [Usage](#usage)
- [Related Projects](#related-projects)
- [Contributing](#contributing)
- [License](#license)

## Features

- 🚀 {{feature 1}}
- 🎯 {{feature 2}}
- 🔧 {{feature 3}}
- {{...}}

## Quickstart

\`\`\`bash
{{fastest path to "it works"}}
\`\`\`

## Installation

{{full install instructions, all platforms/methods}}

## Usage

{{examples, ideally with a second small screenshot or gif if genuinely useful}}

## Related Projects

{{2-4 sentences per related/inspiration project from the research step, each as its own short paragraph or bullet with a link}}

## Contributing

We'd love your help — see [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

## License

[{{License name}}](LICENSE)
```

---

## 3. Classic Technical Docs

**Best for:** libraries/APIs with real configuration surface area, projects being evaluated by engineers for production use, anything where thoroughness signals trustworthiness.

**Tone:** Precise, complete, neutral. Longer TOC, more nested headers, tables over prose where possible.

```markdown
# {{Project Name}}

{{2-3 sentence description: what it is, what problem it solves, what makes it different}}

[![License](https://img.shields.io/github/license/{{owner}}/{{repo}})](LICENSE)
[![Build](https://img.shields.io/github/actions/workflow/status/{{owner}}/{{repo}}/{{workflow}}.yml)]({{ci_url}})
[![Version](https://img.shields.io/{{registry}}/v/{{package}})]({{package_url}})
[![Docs](https://img.shields.io/badge/docs-latest-blue)]({{docs_url}})

## Table of Contents

- [Overview](#overview)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Architecture](#architecture)
- [FAQ](#faq)
- [Contributing](#contributing)
- [Related Projects](#related-projects)
- [License](#license)

## Overview

{{what it does, design philosophy, when to use it vs. not}}

## Requirements

| Requirement | Version |
|---|---|
| {{runtime}} | {{version}} |
| {{dependency}} | {{version}} |

## Installation

\`\`\`bash
{{install command(s) for each supported method}}
\`\`\`

## Quickstart

\`\`\`{{lang}}
{{minimal working example}}
\`\`\`

## Configuration

| Option | Type | Default | Description |
|---|---|---|---|
| {{option}} | {{type}} | {{default}} | {{description}} |

## API Reference

{{full or linked reference}}

## Architecture

{{brief explanation of how it works internally, if relevant to adopters}}

## FAQ

**{{question}}**
{{answer}}

## Contributing

{{guidelines, or link to CONTRIBUTING.md}}

## Related Projects

{{research-step content: alternatives, prior art, what inspired it}}

## License

[{{License name}}](LICENSE)
```

---

## 4. Startup / Product Landing

**Best for:** projects actively trying to build a user base or contributor community, "show HN"-style launches, tools competing against well-known alternatives.

**Tone:** Marketing-forward but still honest — this is a pitch, not just documentation. Comparison tables and social proof are the signature move.

```markdown
<div align="center">
  <img src="{{logo path}}" alt="{{Project Name}} logo" width="100" />

  # {{Project Name}}

  ### {{bold value-proposition tagline}}

  {{one paragraph: the problem, and how this solves it}}

  [![License](https://img.shields.io/github/license/{{owner}}/{{repo}})](LICENSE)
  [![Stars](https://img.shields.io/github/stars/{{owner}}/{{repo}}?style=social)]({{repo_url}})

  [**Get Started**](#quickstart) · [**Live Demo**]({{demo_url}}) · [**Join the community**]({{discord_or_community_url}})

</div>

## Table of Contents

- [Why {{Project Name}}?](#why-projectname)
- [Quickstart](#quickstart)
- [How It Compares](#how-it-compares)
- [Features](#features)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

## Why {{Project Name}}?

{{the problem this solves, and the "aha" moment}}

## Quickstart

\`\`\`bash
{{fastest path to a working result}}
\`\`\`

## How It Compares

| | {{Project Name}} | {{Alternative A}} | {{Alternative B}} |
|---|---|---|---|
| {{criterion}} | ✅ | ⚠️ | ❌ |
| {{criterion}} | ✅ | ✅ | ⚠️ |

*Comparisons reflect {{date}} and are based on public documentation — corrections welcome via issue/PR.*

## Features

- {{feature 1}}
- {{feature 2}}

## Roadmap

- [ ] {{planned feature}}
- [x] {{shipped feature}}

## Contributing

{{call to action — this design leans on community energy}}

## License

[{{License name}}](LICENSE)
```

---

## Cross-design notes

- **Comparison tables** (design 4, or added to any design): always base claims on what you actually found via research (Step 3 of SKILL.md), state the comparison date, and stay factual — no disparagement, and mark it correctable.
- **Logos/screenshots** the user doesn't have yet: use an HTML comment placeholder, e.g. `<!-- TODO: replace with real screenshot at assets/demo.png -->`, and keep the `<img>` tag structure so they can drop the file in later.
- **Badge shields**: see `references/seo-and-structure.md` for exact shields.io URL patterns — never hand-roll a badge image from memory, the query-param syntax matters.