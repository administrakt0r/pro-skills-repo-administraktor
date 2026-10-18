# Coding Guidelines Generator

An AI agent skill for deterministically detecting technology stack layers,
generating concise curated guideline files, and linking them from `AGENTS.md`
without overwriting user content.

## What It Does

Skills do not auto-run on installation. When explicitly invoked in a repository,
this skill:

1. **Detects**: Runs a deterministic, stdlib-only Python script (`detect_stack.py`)
   to identify project languages, frameworks, versions, and verified build/test/lint
   commands without network calls.
2. **Confirms**: Presents the detected configuration and proposed guideline
   files to the user before writing anything.
3. **Generates**: Produces tailored `AGENTS-GUIDELINES-{STACK}.md` files containing
   only rules relevant to detected layers, protected by metadata markers.
4. **Links**: Upserts a clean, concise (under 12 lines) routing block into
   the repository's `AGENTS.md`.
5. **Preserves**: Hand edits outside markers are never overwritten. Re-running on
   an unchanged repo is byte-identical.

## Supported Stacks & Layering

| Primary Stack | Layers Added | Output Guideline File | Reference |
| :--- | :--- | :--- | :--- |
| **Android** | Kotlin / Java, Compose, Coroutines, Room | `AGENTS-GUIDELINES-ANDROID.md` | `references/android.md` |
| **JavaScript / Node.js** | Module format (ESM/CJS), async error boundaries | `AGENTS-GUIDELINES-JS.md` | `references/javascript.md` |
| **TypeScript** | Strict mode, boundary validation | `AGENTS-GUIDELINES-JS.md` | `references/typescript.md` |
| **React** | Hooks rules, derived state, WCAG AA a11y | `AGENTS-GUIDELINES-REACT.md` | `references/react.md` |
| **Next.js** | Server Components, Server Actions auth, cache | `AGENTS-GUIDELINES-NEXTJS.md` | `references/nextjs.md` |
| **Python** | Type hints, pathlib, parameterized SQL (+ FastAPI/Django/Flask) | `AGENTS-GUIDELINES-PYTHON.md` | `references/python.md` |
| **PHP** | Strict types, PSR-12, PDO prepared statements | `AGENTS-GUIDELINES-PHP.md` | `references/php.md` |
| **WordPress** | Nonces, capabilities, sanitization/escaping, REST | `AGENTS-GUIDELINES-WORDPRESS.md` | `references/wordpress.md` |
| **Go** | Gofmt, `%w` error wrapping, context propagation | `AGENTS-GUIDELINES-GO.md` | `references/go.md` |
| **Rust** | Result/Option `?` propagation, unsafe invariants | `AGENTS-GUIDELINES-RUST.md` | `references/rust.md` |
| **Shell** | Strict mode, quoting, portable conditionals | `AGENTS-GUIDELINES-SHELL.md` | `references/shell.md` |
| **HTML / CSS** | Native semantic elements, WCAG AA contrast | `AGENTS-GUIDELINES-HTML-CSS.md` | `references/html-css.md` |
| **Java / Kotlin** | Backend JVM, JUnit 5, nullability | `AGENTS-GUIDELINES-JAVA.md` | `references/java.md` |
| **Generic / Unknown** | Portable engineering standards fallback | `AGENTS-GUIDELINES-GENERIC.md` | `references/generic.md` |

## Monorepo Collision Resolution

- If a package directory contains its own `AGENTS.md`, guideline files are generated
  next to that package's `AGENTS.md`.
- Otherwise, guidelines are generated once per stack next to the root `AGENTS.md`,
  listing the directories each file covers.

## Invocation

Skills do not auto-run. Trigger this skill by telling your agent:

```text
Set up agent guidelines for this repository
```
or
```text
Detect my stack and generate AGENTS.md coding rules
```

Modes supported:
- **Default**: Detect, confirm, generate guidelines, and link from `AGENTS.md`.
- **Dry-run**: Show planned diffs without modifying files (`--dry-run`).
- **Remove**: Cleanly detach markers and guidelines (`--remove`).

## Structure

```text
skills/development-skills/coding-guidelines-generator/
├── SKILL.md                  # Lightweight routing instructions (< 150 lines)
├── README.md                 # You are here
├── scripts/
│   ├── detect_stack.py       # Stdlib-only deterministic detector
│   └── upsert_section.py     # Marker-based upsert with hash & diff support
├── references/               # Modular per-stack guideline references
│   ├── android.md
│   ├── javascript.md
│   ├── typescript.md
│   ├── react.md
│   ├── nextjs.md
│   ├── python.md
│   ├── php.md
│   ├── wordpress.md
│   └── ...
├── assets/
│   ├── baseline.md           # Portable baseline
│   └── agents-md-section.md  # Template link block for AGENTS.md
└── tests/
    └── run_tests.py          # Fixture-based test suite (19 fixtures + upsert tests)
```

## Installation

Install the complete directory into your agent's skills directory so all
scripts, assets, and references remain intact:

```bash
# OpenCode
mkdir -p ~/.config/opencode/skills
cp -R skills/development-skills/coding-guidelines-generator \
  ~/.config/opencode/skills/coding-guidelines-generator

# Codex
mkdir -p ~/.codex/skills
cp -R skills/development-skills/coding-guidelines-generator \
  ~/.codex/skills/coding-guidelines-generator

# Claude Code
mkdir -p ~/.claude/skills
cp -R skills/development-skills/coding-guidelines-generator \
  ~/.claude/skills/coding-guidelines-generator
```

## License

See repository [LICENSE](../../../LICENSE).
