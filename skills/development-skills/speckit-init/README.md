# speckit-init

An AI agent skill for bootstrapping, configuring, and maintaining
[GitHub Spec Kit](https://github.com/github/spec-kit) in any repository.

## What it does

This skill guides an AI agent through the full Spec Kit initialization
lifecycle — from first install through constitution authoring, guide
creation, and ongoing maintenance — producing a truthful, codebase-specific
setup rather than a generic template.

### Covers

- **Installation & health checks** — detect CLI, install if missing, verify integration status
- **Agent integration detection** — enumerate actual commands/skills from the manifest, not hard-coded lists
- **Constitution authoring** — derive governance rules from the repo's own docs
- **SPECKITINIT.md creation** — full operator manual with command reference, pipelines, recipes, verification matrix
- **Update automation** — advisory update checker with native task runner integration
- **Ownership tracking** — classify files as managed, user-authored, generated-but-customizable, or unknown

### Does NOT cover

- Implementing application features (that's `speckit.implement` or equivalent)
- Writing application code, tests, or migrations
- Deploying or publishing anything

## Installation

Install the complete directory so the skill can retain any future supporting
resources. For Codex, the default skill directory is `~/.codex/skills`:

```bash
mkdir -p ~/.codex/skills
cp -R skills/development-skills/speckit-init ~/.codex/skills/speckit-init
```

During local development, use a symlink instead:

```bash
mkdir -p ~/.codex/skills
ln -s "$(pwd)/skills/development-skills/speckit-init" \
  ~/.codex/skills/speckit-init
```

For OpenCode, Claude, or another agent, install the directory in that agent's
documented skills location. The Spec Kit command syntax is integration-specific;
the skill detects and documents the syntax available in the target repository.

## Usage

Invoke from your agent when you need to:

- Set up Spec Kit in a new or existing project
- Create or update `SPECKITINIT.md`
- Author or amend a project constitution
- Check for Spec Kit CLI updates
- Audit the current integration status

### Example prompts

```
Initialize Spec Kit in this project
```

```
Create a SPECKITINIT.md operator manual for this repo
```

```
Check if my Spec Kit CLI is up to date
```

```
Write a constitution for this project based on the existing docs
```

## Structure

```
skills/development-skills/speckit-init/
├── SKILL.md      # The skill definition (follow this)
└── README.md     # You are here
```

## Key design decisions

| Decision | Rationale |
|----------|-----------|
| Framework-agnostic, not framework-unaware | Detect the real stack first; never copy assumptions from another project |
| Agent-neutral first, adapter second | Spec Kit concepts are universal; invocation syntax varies by agent |
| Output is a runbook, not a cheatsheet | `SPECKITINIT.md` should be followable by a new contributor without guessing |
| Advisory updates only | Never silently rewrite project files, upgrade deps, or deploy |
| Idempotent | Running the skill twice converges to the same result |

## Requirements

- [Spec Kit CLI](https://github.com/github/spec-kit) (`uv tool install specify-cli`)
- A repository the agent can inspect
- An AI agent that supports skills (OpenCode, Codex, Claude, etc.)

## License

See the [MIT license](https://github.com/administrakt0r/pro-skills-repo-administraktor/blob/main/LICENSE).
