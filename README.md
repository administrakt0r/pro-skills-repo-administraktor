# Pro Skills Repository

Practical, agent-ready skills for repeatable technical workflows. Each skill
is a self-contained `SKILL.md` that gives an AI coding agent task-specific
operating guidance without prescribing a particular framework or stack.

## Skills

| Skill | Use it for | Location |
| --- | --- | --- |
| `speckit-init` | Installing, initializing, documenting, and maintaining [GitHub Spec Kit](https://github.com/github/spec-kit) in an existing repository. | [`skills/development-skills/speckit-init`](skills/development-skills/speckit-init/) |
| `linux-speed-optimizer` | Evidence-led, approval-gated Linux performance analysis and tuning. | [`skills/system-administration-skills/linux-speed-optimizer`](skills/system-administration-skills/linux-speed-optimizer/) |

## Spec Kit resources

The framework- and agent-neutral [Spec Kit workflow guide](speckit-skills-guides-workflows/SPECKIT-workflows.md) explains the full specification-driven development cycle, optional stages, maintenance, and safety boundaries. Use it as a reusable reference; keep project-specific facts in that project’s `SPECKITINIT.md`.

## Install a skill

Clone this repository, then copy the skill directory into your agent’s skill
location. For Codex, the default location is `~/.codex/skills`:

```bash
git clone https://github.com/administrakt0r/pro-skills-repo-administraktor.git
mkdir -p ~/.codex/skills
cp -R pro-skills-repo-administraktor/skills/development-skills/speckit-init \
  ~/.codex/skills/speckit-init
```

For another agent, place the complete skill directory (not only `SKILL.md`) in
that agent’s documented skills directory. See each skill’s README for its
scope, prerequisites, and examples.

## Design principles

- Inspect the real environment before recommending a change.
- Keep repository-specific facts separate from reusable guidance.
- Require explicit approval before consequential system or project mutations.
- Prefer evidence, reversible changes, and clear verification over generic recipes.

## Contributing

Keep skills narrowly scoped, use a discriminating `name` and `description`, and
include only instructions that materially improve an agent’s decisions. Test
new guidance against realistic requests and avoid hard-coding version-sensitive
commands unless they have been verified.

## License

[MIT](LICENSE)
