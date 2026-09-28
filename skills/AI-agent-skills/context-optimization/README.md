# context-optimization

An AI agent skill for getting more work out of a fixed context window.
Covers compaction, observation masking, cache-friendly prompt layout, and
context partitioning, for an agent managing its own session and for code that
builds agent systems.

## What it does

Guides an agent through choosing and applying the right context technique for
where the tokens are going, then measuring whether the change helped.
Every technique ships with a retention rule that says what must never be
compressed away.

### Covers

- **Compaction.** Summarize a full window and reopen seeded with the summary.
  Compression order, per-source summary recipes, and the list of state that must
  survive every compaction.
- **Observation masking.** Replace digested tool output with a short reference
  and extracted findings. A three-tier retention policy (never, consider, always)
  and a worksheet that decides each case.
- **Cache-friendly layout.** Order context from most stable to most variable so
  prefix caching hits, with a worked example and the two rules that
  break it.
- **Context partitioning.** Split exploration across sub-agents with clean
  windows. Three patterns (map then reduce, staged pipeline, isolated review) and
  a five-part sub-agent brief.
- **Budgets.** Token allowances per category, a reserved response buffer, and
  degradation signals that tell you the window has stopped holding the task.

### Does NOT cover

- RAG retrieval design or vector database selection
- Training, fine-tuning, or model architecture
- Deciding which model to use

## Installation

Copy the whole directory, not only `SKILL.md`, so the skill keeps its
`references/` folder.

```bash
git clone https://github.com/administrakt0r/pro-skills-repo-administraktor.git
mkdir -p ~/.config/opencode/skills
cp -R pro-skills-repo-administraktor/skills/AI-agent-skills/context-optimization \
  ~/.config/opencode/skills/context-optimization
```

OpenCode reads skills from `~/.config/opencode/skills` and also picks up
`~/.claude/skills` and `~/.agents/skills`. Claude Code reads from
`~/.claude/skills`. Codex reads user skills from `~/.agents/skills` and
repository skills from `.agents/skills`. Other agents have their own documented
location; place the complete directory there.

## Files

| File | Purpose |
| --- | --- |
| `SKILL.md` | Technique selection and operating rules |
| `references/optimization-techniques.md` | Summary recipes, worksheets, worked examples, failure modes, provider cache and compaction mechanics |

## Provenance

Adapted from `context-optimization` in
[AI-Agents-Safe-Coding-Skills](https://github.com/administrakt0r/AI-Agents-Safe-Coding-Skills),
originally dated 2025-12-20.

Changes from the upstream version:

- The upstream file linked to sibling skills (`context-fundamentals`,
  `context-degradation`, `evaluation`, `memory-systems`, `multi-agent-patterns`)
  and to an internal reference that shipped with neither. Those links are gone.
  The promised reference now exists as `references/optimization-techniques.md`.
- Guidance is split by audience. An agent reading this now has moves it can make
  in its own session, separate from advice for building agent systems.
- Upstream performance figures had no source. They are labeled as planning
  targets to validate on your own workload.
- Frontmatter carries only `name` and `description`, matching this repository.
  The upstream `risk` and `source` fields are not part of the skill format in use
  here, so provenance moved into this file.
