# Optimization Techniques Reference

Working detail behind `SKILL.md`. Read the section that matches the technique you
are about to apply.

## 1. Compaction summary recipes

A summary is only useful if it preserves what the next step needs. Write to these
templates.

### Tool output

```
[tool] <command or query>
[key findings] <the facts that changed a decision>
[values] <numbers worth keeping: counts, sizes, timings, versions>
[open] <anything the output raised but did not answer>
```

Drop progress meters, ANSI noise, repeated headers, stack frames above the root
cause, and log lines that repeat a known state.

### Conversation turns

```
[decided] <decision> because <reason>
[constraint] <what the work must not break or must respect>
[done] <completed step> -> <result>
[next] <the following step and why>
```

Drop greetings, apologies, retries that reached the same answer, and questions
already answered.

### Retrieved documents and files

```
[claim] <fact> from <source path or URL>
[value] <config value, version, API shape, or constant>
[not verified] <claim that was asserted but never checked>
```

Drop restated introductions, marketing framing, and examples that repeat a claim
already captured.

### What must survive every compaction

Write these down before triggering compaction, and restore them after:

- The goal of the current task.
- Constraints the user gave that the work must respect.
- Files and symbols already changed, with paths.
- Decisions made and the reason for each.
- Errors still unresolved and what was ruled out.
- The next concrete step.

## 2. Masking retention worksheet

| Question | Yes | No |
| --- | --- | --- |
| Is the current step reasoning over this output? | Never mask | Continue |
| Is it from the most recent turn? | Never mask | Continue |
| Does it hold an unresolved error? | Never mask | Continue |
| Are its findings already recorded elsewhere? | Always mask | Continue |
| Has its purpose been served and is it from 3+ turns back? | Mask | Continue |
| Is it repeated output or boilerplate? | Always mask | Keep |

Masked entry format:

```
[Obs <ref-id>] <command or query>
Key: <2-4 findings that mattered>
Full output retrievable via <reference>
```

## 3. Cache-ordering template

Place content in this order. Anything higher must be stable across every request
in the session.

```text
1. system prompt          stable for the whole session
2. tool definitions       stable for the whole session
3. fixed instructions     stable for the whole session
4. schemas, templates     stable within a workflow
5. retrieved context      stable within a task
6. conversation history   appended only
7. current task           appended last
```

Worked example. Two turns of a session that reads a repository and proposes a
change:

```text
Turn 1: [system prompt][tool defs][repo overview][user question]
Turn 2: [system prompt][tool defs][repo overview][user question][file slice][agent reply]
```

Turn 2 reuses the cached prefix through the user question. The new material is
appended, so the prefix hash is unchanged and the cache hits.

Counter-example, where the cache breaks:

```text
Turn 1: [system prompt][run 14:02:11][repo overview][user question]
Turn 2: [system prompt][run 14:07:49][repo overview][user question][file slice]
```

The timestamp sits inside the prefix, so every turn produces a different prefix
hash and nothing is reused. Put the timestamp in the final block or leave it out.

Two rules follow. Append rather than insert, and keep volatile values out of the
leading region.

## 4. Partitioning patterns

### Map then reduce

Fan out one bounded subtask per sub-agent, then merge.

```
coordinator -> sub-agent A  (search area 1) -> findings A
            -> sub-agent B  (search area 2) -> findings B
            -> sub-agent C  (search area 3) -> findings C
            -> merge findings A+B+C -> answer
```

Use for repository sweeps, doc surveys, and anything where the answer is much
smaller than the material searched.

### Staged pipeline

Each sub-agent hands a narrow artifact to the next stage.

```
explore -> [facts] -> analyze -> [recommendation] -> draft -> [deliverable]
```

Use when each stage has a genuinely small interface. If the interface is large,
the pipeline saves nothing.

### Isolated review

One sub-agent produces work in the main window, a second reviews it with a clean
window and no exposure to the producing reasoning.

```
main -> [artifact] -> reviewer (clean context) -> [findings]
```

Use when the reviewer must not inherit the author's assumptions.

### Sub-agent brief

Every sub-agent gets the same five parts:

```
[question]    the single question to answer
[scope]       paths, directories, or sources to inspect
[constraints] what not to change, what not to assume
[format]      the exact shape of the returned findings
[limits]      what to do if the answer is not found
```

## 5. Budget worksheet

Fill this in before starting the work, then track against it.

| Category | Allowance | Actual | Notes |
| --- | --- | --- | --- |
| System prompt | | | stable, cached |
| Tool definitions | | | stable, cached |
| Retrieved material | | | summarize or mask first |
| Message history | | | compact at threshold |
| Response buffer | | | never spend this |
| **Total** | | | must stay under the window |

Reserve the response buffer first. A window filled to 100 percent leaves
nowhere to put the answer.

## 6. Degradation checklist

Run these when a long session starts producing worse answers:

- Does the agent re-read files it already read? History was compacted too far.
- Do answers contradict earlier turns? Decisions were dropped from a summary.
- Did a stated constraint stop being enforced? Constraints did not survive compaction.
- Are tool results being re-fetched and re-parsed? Masking dropped retrievable references.
- Did cost per turn climb while content stayed similar? The cached prefix is unstable.

Each signal points at a specific fix: keep more history, write better summaries,
carry constraints forward explicitly, retain references, or stabilize the prefix.

## 7. Failure modes

| Mistake | Result | Fix |
| --- | --- | --- |
| Compressing the system prompt | Every behavior changes mid-task | Keep it intact |
| Masking before the agent uses the output | Decisions made on missing data | Mask after the decision |
| Summarizing without keeping references | Findings cannot be checked | Store the reference with the summary |
| Compacting at the limit | No room to write the summary | Trigger at the threshold |
| Merging partitions without checking coverage | Silent gaps in the answer | Confirm every partition returned |
| Unstable prefix content | Cache hit rate near zero | Append, keep volatility last |
