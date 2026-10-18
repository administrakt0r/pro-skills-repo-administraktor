# Coding Guidelines Generator

**Type**: Antigravity Skill  
**Category**: Development Skills  
**Skill Name**: `coding-guidelines-generator`

## What It Does

Automatically generates stack-specific coding guideline files for any
repository. The skill:

1. **Auto-detects** the project's tech stack(s) by scanning for signature
   files (package.json, go.mod, Cargo.toml, etc.)
2. **Inspects** the actual project configuration (linters, formatters, test
   runners, build tools) to produce tailored, actionable rules
3. **Generates** per-stack `AGENTS-GUIDELINES-{STACK}.md` files next to
   AGENTS.md
4. **Merges** with existing guideline files, preserving all user customizations
   and adding only missing sections
5. **Injects** a mandatory read-and-obey directive at the top of AGENTS.md
   (idempotent — won't duplicate if already present)

## Supported Stacks

| Stack | Output File | Signature Files |
|-------|-------------|-----------------|
| JavaScript/TypeScript | `AGENTS-GUIDELINES-JS.md` | package.json, tsconfig.json, etc. |
| Python | `AGENTS-GUIDELINES-PYTHON.md` | pyproject.toml, requirements.txt, etc. |
| Go | `AGENTS-GUIDELINES-GO.md` | go.mod, go.sum |
| Rust | `AGENTS-GUIDELINES-RUST.md` | Cargo.toml, Cargo.lock |
| PHP | `AGENTS-GUIDELINES-PHP.md` | composer.json, artisan, wp-config.php |
| Java/Kotlin | `AGENTS-GUIDELINES-JAVA.md` | build.gradle, pom.xml, gradlew |
| Shell/Bash | `AGENTS-GUIDELINES-SHELL.md` | *.sh in root, Makefile |
| HTML/CSS | `AGENTS-GUIDELINES-HTML-CSS.md` | index.html, tailwind.config.* |
| Generic (fallback) | `AGENTS-GUIDELINES-GENERIC.md` | (unknown stacks) |

Multi-stack projects get separate files for each detected stack.

## Guideline Categories

Each generated file covers these 10 areas:

1. Package Manager & Lockfile
2. Linting & Formatting
3. Type Safety & Nullability
4. Testing Conventions
5. Error Handling
6. Security Patterns
7. Build & Compilation
8. Dependency Management
9. Logging & Observability
10. API Design

## How to Trigger

Ask the AI agent to:

- "Generate coding guidelines for this project"
- "Set up coding rules for this repo"
- "Create project standards"
- "Add AGENTS-GUIDELINES files"
- "Bootstrap coding conventions"

The skill activates automatically when the request matches these patterns.

## Installation

Copy the `coding-guidelines-generator/` folder into one of:

- **Global**: `~/.gemini/config/skills/coding-guidelines-generator/`
- **Workspace**: `{repo}/.gemini/skills/coding-guidelines-generator/`

The folder must contain the `SKILL.md` file.

## What It Produces

### In the target repository:

```
project-root/
├── AGENTS.md                        # Directive prepended at top
├── AGENTS-GUIDELINES-JS.md          # (if JS/TS detected)
├── AGENTS-GUIDELINES-PYTHON.md      # (if Python detected)
├── AGENTS-GUIDELINES-GO.md          # (if Go detected)
└── ...                              # one per detected stack
```

### Directive block (prepended to AGENTS.md):

```markdown
<!-- CODING-GUIDELINES-DIRECTIVE -->
> [!IMPORTANT]
> **Mandatory Coding Guidelines**
>
> Before starting ANY work in this repository, you MUST read and obey the
> following stack-specific coding guideline files.
>
> - AGENTS-GUIDELINES-JS.md — JavaScript/TypeScript rules
> - AGENTS-GUIDELINES-PYTHON.md — Python rules
>
> Violations must be corrected before completing any task.
<!-- /CODING-GUIDELINES-DIRECTIVE -->
```

### Completion report includes:

- Stacks detected (with signature files)
- Files created, merged, or skipped
- AGENTS.md status
- Project tools found

## Key Design Decisions

- **Idempotent**: Running twice produces the same result. No duplicates.
- **Non-destructive**: Never overwrites user content. Merges additions only.
- **Tailored, not generic**: Inspects actual project config to reference real
  tools and commands.
- **Concise**: 200-400 words per guideline file to conserve agent context.
- **Self-contained**: Embeds the portable baseline so it works without any
  global configuration installed.
- **Git-safe**: Does not stage or commit changes.

## Foundation

Built on a proven portable baseline covering: smallest complete changes,
repository convention adherence, input validation, server-side authorization,
secret protection, proportionate verification, accurate outcome reporting,
and authorized-only destructive actions.

## License

See repository [LICENSE](../../LICENSE).
