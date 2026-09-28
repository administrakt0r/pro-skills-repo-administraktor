---
name: context-optimization
description: Use when a task risks running out of context window, when a long-running agent session or multi-step workflow must stay coherent across many turns, when token cost or latency climbs with conversation length, or when the user asks about compaction, summarizing conversation history, truncating tool output, KV-cache or prefix caching, cache-friendly prompt ordering, context budgets, or splitting work across sub-agents. Covers compaction, observation masking, cache-aware layout, and context partitioning, both for an agent managing its own session and for code that builds agent systems. Do not use for RAG retrieval design or vector database selection.
---

# Context Optimization

Context optimization extends what fits in a fixed context window. It works through
four moves: compaction, observation masking, cache-aware layout, and context
partitioning. Pick the move that matches where the tokens go.

Measure before you optimize. Without a rough picture of what fills the window,
compression tends to remove the wrong material and keep the noise.

## Pick the move from the symptom

| Where the tokens go | Apply |
| --- | --- |
| Tool output and command results | Observation masking |
| Long conversation history | Compaction |
| Retrieved documents or large files | Summarize, then partition |
| Repeated system prompt and tool definitions | Cache-aware layout |
| Several unrelated subtasks in one window | Context partitioning |

Trigger optimization when utilization passes roughly 70 percent, when answer
quality drops as a session lengthens, or when cost and latency climb with
conversation length. Treat 70 percent as a planning heuristic and reserve
headroom for the response itself. Quality can also decay before the window
fills: recall and instruction-following weaken as the window grows, so a
session that has stopped holding the task needs attention even with room to
spare.

## Compaction

Compaction summarizes a context window and reopens a fresh window seeded with
that summary. Use it when conversation history dominates.

Compress in this order, cheapest loss first:

1. Tool output that has been read and acted on.
2. Old turns, reduced to decisions and commitments.
3. Retrieved documents, when the distilled facts will do.

Never compress the system prompt, active task state, open file paths, unresolved
errors, or anything the next action depends on.

Summaries preserve different material depending on where they came from:

| Source | Keep | Drop |
| --- | --- | --- |
| Tool output | findings, numbers, conclusions | raw logs, headers, progress noise |
| Conversation | decisions, commitments, constraints, context shifts | greetings, retries, filler |
| Documents | claims, facts, configuration values | supporting argument, repeated examples |

If the runtime ships a built-in compact or compress command, use it instead of
writing a summarizer. It already knows the message boundaries. Before triggering
it, write down what the session must not lose: the current goal, the files
touched, the decisions made, and the next step. After compaction, re-read that
list and restore anything the summary dropped.

Compaction is lossy by design, and most runtimes keep a slice of the most recent
conversation beside the summary rather than compacting everything. Widen that
slice when recent detail matters more than reclaiming space. When the platform
can compact or clear old tool results on its side — server-side context
management that runs before token counting and cache lookup — prefer it to
hand-rolled trimming: it is tuned to the runtime and leaves the cached prefix
intact.

## Observation masking

Tool output can fill most of a long agent trajectory, and most of it has already
done its job once the agent has acted on it. Masking replaces the verbose output
with a short reference plus the extracted findings.

Retention policy:

- **Never mask** output the current step is reasoning over, output from the most
  recent turn, or anything holding an error still under investigation.
- **Consider masking** output from three or more turns back whose findings are
  already recorded, verbose output whose key points extract cleanly, and output
  whose purpose has been served.
- **Always mask** repeated output, boilerplate headers and footers, and output
  already summarized elsewhere in the conversation.

Store the original before masking so a reference can retrieve it. A masked entry
should stand alone: the command or query that produced it, the key findings, and
the reference to the full output.

## Cache-friendly layout

Prefix caching reuses the computed key and value tensors for any request sharing
a leading prefix with an earlier one. Requests that share a long prefix cost less
and answer faster.

Order the context from most stable to most variable:

1. System prompt and tool definitions.
2. Reused templates, schemas, and fixed instructions.
3. Session-specific content and the current task.

Cache hits depend on stability. Keep formatting consistent, keep timestamps and
random identifiers out of the cached region, and append new content rather than
rewriting what precedes it. When the system prompt must change, change it at the
end rather than at the beginning.

Caching is provider-side and conditional, so confirm the mechanics rather than
assuming them. A prefix usually caches only above a minimum size — commonly
around 1,024 tokens, higher for some models — and it must match the earlier
request byte for byte. Cached entries expire after a short idle window, roughly
five minutes and refreshed on use, with longer lifetimes available on some
providers. Writes can cost more than uncached input while reads are heavily
discounted, so a prefix that never hits is pure overhead. Measure the real hit
rate from the provider's usage fields — cached or cache-read input tokens —
before trusting any target.

## Context partitioning

Partitioning splits work across sub-agents that each hold a clean, narrow window.
Use it when a task needs a lot of exploration to produce a small result: searches,
file sweeps, comparisons, and large document reading.

Give each sub-agent the question to answer, the constraints it must respect, and
a fixed output format. It returns findings rather than its transcript. The
coordinator keeps the synthesis and drops the search detail.

Before merging, confirm that every partition returned. Merge compatible findings,
and summarize if the merged result still does not fit. Handle failures per
partition: retry the missing one rather than the whole task.

## Budgets

Set explicit token allowances per category before work starts: system prompt,
tool definitions, retrieved material, message history, and a reserved buffer for
the response. Track usage against those allowances during the work instead of
discovering the limit at the point of failure.

Three symptoms show the window has stopped holding the task. The agent re-reads
files it already processed, answers contradict earlier turns, and constraints
quietly stop being enforced.

## When you are the agent

You can apply all of this to your own session:

- Read files in slices sized to the question at hand rather than loading whole
  files.
- Delegate bounded exploration to sub-agents and keep their conclusions.
- Drop tool output you have already digested instead of carrying it forward.
- Trigger compaction early in a long session instead of at the moment of failure.
- Re-state the goal, constraints, and next step after any compaction.

## When you build agent systems

- Mask tool output where it stops being needed, not at ingestion. Masking early
  removes output the agent has not used yet.
- Write the system prompt as a stable prefix and keep dynamic state out of it.
- Track token utilization per category and expose it so operators can see where
  the window goes.
- Degrade in the open. When compaction fails or the window fills anyway, report
  the state rather than silently losing task context.

## Targets to measure against

These are planning figures to validate on your own workload, not published
measurements. Record what you measure and adjust.

| Technique | Target |
| --- | --- |
| Compaction | 50 to 70 percent token reduction |
| Observation masking | 60 to 80 percent reduction in masked observations |
| Cache-friendly layout | 70 percent or better hit rate on stable workloads |

Track quality alongside token counts, and reject any setting where task success
drops.

## Reference file

`references/optimization-techniques.md` holds the detail that would crowd this
file: summary recipes per content type, a masking retention worksheet, a
cache-ordering template with a worked example, partitioning patterns, a budget
worksheet, the degradation checklist, a failure-mode table, and provider cache
and compaction mechanics.
