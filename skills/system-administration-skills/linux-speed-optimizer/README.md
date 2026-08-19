# linux-speed-optimizer

An AI agent skill for analyzing and safely optimizing Linux system
performance — laptops, desktops, and servers. Distro-agnostic, idempotent,
and approval-gated: the agent analyzes first, proposes a risk-labeled plan,
and applies **only** the changes you approve.

## What it does

Guides an AI agent through a complete system-performance audit and
optimization lifecycle: hardware/kernel analysis → prioritized proposal →
approved, idempotent application → per-change verification → documented
rollback.

### Covers

- **Full system analysis** — CPU, RAM/memory pressure, swap & zram, storage
  (SSD/HDD, mount options, trim), boot timeline, services, GPU & compositor,
  thermals & power, network, and any pre-existing tuning
- **Memory & swap tuning** — zram sizing/algorithm, swappiness, cache
  pressure, page-cluster, writeback tuning (only when the analysis justifies it)
- **Boot & services cleanup** — GRUB timeout, wait-online/ModemManager-style
  units, per-service disable decisions with boot/RAM costs shown
- **Kernel & GPU params** — safe GRUB cmdline additions (e.g. i915 FBC),
  latency vs. battery tradeoffs labeled, security tradeoffs gated behind
  explicit approval
- **OOM protection** — earlyoom/systemd-oomd enabled in real kill mode
- **Optional custom kernel** — XanMod / Liquorix / linux-zen installs with
  CPU microarchitecture-level checks, Secure Boot checks, distro fallback
  kernel preserved, and revert documentation
- **Hardware advice** — honest recommendations (e.g. "add RAM") that are
  reported, never applied

### Does NOT cover

- Application or website performance (no app code, no web tuning)
- Container/Docker performance tuning
- Destructive operations (formatting, fstab rewrites, partition resizing)
- Anything without explicit user approval

## Installation

Copy `SKILL.md` into your agent's skill directory:

```bash
# OpenCode (global)
mkdir -p ~/.config/opencode/skills/linux-speed-optimizer
cp SKILL.md ~/.config/opencode/skills/linux-speed-optimizer/SKILL.md

# Claude Code / Codex / agents using ~/.claude/skills/ or ~/.agents/skills/
mkdir -p ~/.claude/skills/linux-speed-optimizer
cp SKILL.md ~/.claude/skills/linux-speed-optimizer/SKILL.md
```

Or symlink it so updates to this repo propagate automatically:

```bash
ln -s "$(pwd)/SKILL.md" ~/.config/opencode/skills/linux-speed-optimizer/SKILL.md
```

Restart your agent after installing — skills are loaded at startup.

## Usage

Invoke from your agent whenever you want to make a Linux machine faster:

- "Analyze my laptop and speed it up"
- "Why is my system slow? Run the optimization skill"
- "Tune my kernel and swap settings for responsiveness"
- "What can I safely disable to make boot faster?"

The agent will:

1. **Analyze** (read-only) — full hardware/system sweep, no changes
2. **Propose** — a table of findings with impact/risk/effort, grouped into
   approval packages
3. **Ask** — you approve packages individually via the question prompt
4. **Apply** — only approved changes, each guarded for idempotency
5. **Verify** — every change read back, before/after numbers shown
6. **Report** — what changed, what needs a reboot, exact rollback commands

### Example prompts

```
Run a deep analysis on this laptop and propose speed improvements
```

```
Use the speed optimizer — analyze only, don't change anything yet
```

```
Optimize memory and swap, then disable the services I approve
```

```
Apply the boot and GPU packages, skip the custom kernel
```

### Analyze-only mode

Say "analyze only" or "don't change anything" and the agent will produce the
full findings report without writing a single file.

## Structure

```
skills/linux-speed-optimizer/
├── SKILL.md      # The skill definition (follow this)
└── README.md     # You are here
```

## Key design decisions

| Decision | Rationale |
|----------|-----------|
| Analyze first, approve first | Zero system mutations before the user sees and approves the plan |
| Idempotent recipes | Every action is state-guarded (grep/is-enabled/dpkg checks); re-running converges, never duplicates config or re-installs |
| Distro-aware | apt/dnf/pacman/zypper, zram-tools vs zram-generator, GRUB variants all detected and adapted |
| Evidence over cargo cult | Every sysctl/kernel value must map to an analysis finding; security tradeoffs are labeled and gated |
| Ask per service | Docker, databases, Bluetooth etc. are never blanket-disabled — cost is shown and you decide |
| Rollback always documented | Exact undo commands for every change before it's applied |
| Honest reporting | Expected gains described in real terms, never fabricated benchmarks |

## Requirements

- Linux (systemd assumed; non-systemd init requires adaptation)
- Root/sudo access (the agent will ask you to cache credentials with
  `sudo -v` — it never asks for or stores your password)
- An AI agent that supports skills (OpenCode, Claude Code, Codex, etc.)
- 30–60 seconds of agent analysis time for the audit phase

## License

See the [LICENSE](../LICENSE) file in the repository root.