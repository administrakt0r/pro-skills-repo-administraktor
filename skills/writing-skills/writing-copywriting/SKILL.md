---
name: writing-copywriting
description: >-
  Applies professional writing and copywriting principles across technical documentation,
  developer communications, marketing copy, microcopy, blog articles, changelogs, READMEs,
  and release announcements. Use when drafting, editing, or optimizing any written content
  for clarity, engagement, conversion, and global accessibility.
---

# Writing & Copywriting

A universal skill for crafting clear, persuasive, and technically accurate written content across software development, product marketing, developer relations, and user experience.

---

## When to Use

- Authoring technical documentation: API reference docs, tutorials, system architecture overviews, and developer guides.
- Writing copy for digital products: landing pages, feature announcements, product descriptions, and value propositions.
- Designing user interface microcopy: button labels, error recovery messages, tooltips, onboarding hints, and empty states.
- Producing open-source documentation: README files, contributing guides, and release notes.
- Drafting developer marketing and thought leadership: technical blog posts, case studies, and user stories.
- Creating campaign and transactional communications: email announcements, newsletters, and social media posts.
- Editing, proofreading, or localizing existing copy to improve clarity, voice consistency, and SEO performance.

---

## Prerequisites

- **Target Persona**: Audience identity and technical fluency (e.g., novice programmer, senior systems architect, non-technical executive).
- **Core Objective**: The single primary action or understanding required (e.g., execute a command, install a package, subscribe to updates, resolve a bug).
- **Subject Matter Truths**: Verified facts, runnable code, API parameters, or product capabilities.
- **Voice & Tone Constraints**: Organizational brand guidelines (formality, humor threshold, directness).

---

## Steps

### Step 1: Define Audience and Intent

Before writing, identify the communication context using this decision rubric:

| Dimension | Option A | Option B | Option C |
| :--- | :--- | :--- | :--- |
| **Reader Expertise** | Beginner (needs analogies & context) | Practitioner (needs code & steps) | Architect/Exec (needs trade-offs & outcomes) |
| **Primary Goal** | Educate (tutorial / conceptual doc) | Convert (landing page / CTA copy) | Unblock (error message / troubleshooting) |
| **Consumption Context** | Deep reading (whitepaper / guide) | Skimming (blog post / release note) | Urgent glance (UI dialog / CLI output) |

---

### Step 2: Select the Structural Framework

Match content goals to proven persuasion and structuring frameworks (see [references/writing-frameworks.md](references/writing-frameworks.md) for full templates):

1. **AIDA (Attention, Interest, Desire, Action)**: Ideal for landing pages, product launch announcements, and promotional emails.
   - *Attention*: Disrupt the status quo with a bold metric, provocative question, or counter-intuitive claim.
   - *Interest*: Present relatable challenges, industry realities, and relevant mechanisms.
   - *Desire*: Translate features into tangible transformation and business/developer benefits.
   - *Action*: State a single, unambiguous call to action (CTA).

2. **PAS (Problem, Agitate, Solution)**: Ideal for developer tooling, security products, and workflow optimization solutions.
   - *Problem*: Identify the specific pain point (e.g., flaky tests, broken deployments, schema drift).
   - *Agitate*: Highlight the compounding cost of inaction (wasted engineering hours, midnight alerts, lost revenue).
   - *Solution*: Introduce your system as the definitive, friction-free remedy.

3. **BAB (Before, After, Bridge)**: Ideal for case studies, migration guides, and feature upgrade copy.
   - *Before*: The current inefficient, brittle reality.
   - *After*: The transformed state of speed, reliability, and ease.
   - *Bridge*: The exact method or tool that connects the two.

4. **Inverted Pyramid**: Essential for technical documentation, release notes, and news announcements.
   - Lead with the conclusion, outcome, or most critical fact.
   - Follow with supporting details, prerequisites, and instructions.
   - End with background context, related resources, and edge cases.

---

### Step 3: Apply Core Writing Principles

#### 1. Radical Clarity and Conciseness
- Cut nominalizations (verbs turned into nouns). Replace "perform an analysis of" with "analyze"; replace "facilitate the implementation of" with "implement".
- Eliminate throat-clearing openers ("It is worth noting that", "Needless to say", "In order to").
- Keep sentences between 15–20 words on average. Vary sentence length to establish rhythm.

```markdown
<!-- Poor -->
It is critically important to make sure that you execute the compilation process
in order to facilitate the generation of binary artifacts prior to server deployment.

<!-- Clear & Concise -->
Compile the binary before deploying the server:
`go build -o server ./cmd/server`
```

#### 2. Active Voice and Direct Agency
- Frame instructions with the reader as the active subject.
- Use imperative mood for procedural commands ("Run the script", not "The script should be run").

```markdown
<!-- Passive -->
When the configuration file is saved by the user, the database connection is initialized.

<!-- Active -->
Save the configuration file to initialize the database connection.
```

#### 3. Inverted Pyramid for Reading Habits
- Readers scan in an F-pattern. Front-load key terms into the first two words of headings, bullet points, and paragraphs.
- Keep paragraphs under 4 lines of text.

---

### Step 4: Craft Headlines, Hooks, and Titles

A strong headline communicates value, triggers curiosity, or sets an expectation.

#### Headline Formulas
- **The How-To + Specific Outcome**: `How to [Achieve Desirable Outcome] Without [Common Frustration]`
- **The Numbered System**: `[Number] Ways to [Solve Problem] in [Platform/Language]`
- **The Benchmark / Data Hook**: `Why [Company/Tool] Switched from [A] to [B] (and Cut Latency by 40%)`
- **The Direct Value Proposition**: `[Action Verb] [Target Audience Benefit] in [Timeframe]`

#### Power Words & Sensory Anchors
- *Precision*: Deterministic, zero-allocation, atomic, sub-millisecond, drop-in replacement.
- *Friction Reduction*: Effortless, turnkey, automated, instant, lightweight.
- *Avoid Buzzwords*: Ban terms like "revolutionary", "game-changing", "seamless", "synergy", and "next-generation". Replace them with verifiable measurements and concrete mechanisms.

---

### Step 5: Draft Stack-Specific Content Types

#### A. Technical Documentation & API Docs
- **Structure**: Overview -> Prerequisites -> Quickstart -> Reference -> Error Handling.
- Always document parameters with type, required/optional status, default value, and description.
- Include complete, runnable examples with realistic mock inputs—never truncate essential configuration with unexplained `...`.

```markdown
### `authenticate(token, options)`

Validates a session token against the auth cluster.

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `token` | `string` | Yes | — | JWT bearer token received from client |
| `options.timeoutMs` | `number` | No | `5000` | Network timeout in milliseconds |

**Returns**: `Promise<UserSession>`

**Example**:
```typescript
import { authenticate } from '@service/auth';

const session = await authenticate('jwt_token_here', { timeoutMs: 3000 });
console.log(`Authenticated as user ${session.userId}`);
```
```

#### B. Tutorials & Step-by-Step Guides
- State the finished product and required time upfront.
- Structure steps linearly: Action -> Code snippet -> Expected output -> Verification check.
- Never assume implicit environment variables or secret keys exist without instructions to create them.

#### C. Open Source README Files
Follow the standard 60-second rule:
1. **Header**: Name, clear 1-sentence value proposition, core status badges (build, license, version).
2. **Visual/Demo**: Architecture diagram, terminal screenshot, or 10-second GIF.
3. **Quickstart**: The absolute minimal shell commands to run or test the software.
4. **Key Features**: 3–5 bullet points highlighting differentiation.
5. **Configuration / API**: Core options or basic code usage.
6. **Contributing & License**: Contributing guidelines link, license name.

#### D. Changelogs and Release Notes
Follow [Keep a Changelog](https://keepachangelog.com/) standards:
- Group changes by user impact, not internal commit messages.
- Use categories: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`.
- Mention breaking changes explicitly at the top of the release.

```markdown
## [2.1.0] - 2026-10-06

### Breaking Changes
- `UserClient.connect()` now returns a `Promise<Client>` instead of taking a callback.

### Added
- Support for distributed tracing via OpenTelemetry (`--trace-exporter=otlp`).
- Health check endpoint `/readyz` for Kubernetes ingress probes.

### Fixed
- Memory leak in WebSocket heartbeat ping loop when connection dropped abruptly.
```

#### E. Product Descriptions and Feature Copy
Focus on the progression: **Feature -> Advantage -> Benefit (FAB)**:
- *Feature* (What it is): Distributed write-ahead log.
- *Advantage* (What it does): Replicates transactions across three availability zones before acknowledging.
- *Benefit* (Why the reader cares): Zero data loss during regional cloud outages, keeping your service compliant and online.

#### F. UI Microcopy (Buttons, Errors, Tooltips, Empty States)
Apply the **4-Point Microcopy Rule**:
1. **Clear**: No technical jargon or vague error numbers.
2. **Concise**: Eliminate decorative phrasing.
3. **Useful**: Explain what happened and how to proceed.
4. **Brand-Aligned**: Calm, supportive, and blame-free.

| Element | Weak / Anti-Pattern | Strong / Best Practice |
| :--- | :--- | :--- |
| Primary CTA Button | `Submit` or `Click Here` | `Create API Key` or `Deploy Application` |
| Error Message | `Error 403: Forbidden Action` | `You need Admin permissions to edit billing details. Contact your team owner.` |
| Destructive Action | `Delete` -> `Are you sure?` | `Delete Database` -> `This will delete 3 tables and cannot be undone.` |
| Empty State | `No data available.` | `No deployments yet. Connect your repository to build your first release.` |
| Tooltip | `Click this icon to change settings.` | `API rate limits: 1,000 requests per minute.` |

#### G. Email Copywriting
- **Subject Line**: 35–50 characters. Front-load benefit or novelty. Avoid spam triggers (ALL CAPS, excessive exclamation points, "FREE $$$").
- **Preview Text**: 40–80 characters. Extends and contextualizes the subject line.
- **Body**: Single goal rule. Lead with the core message in paragraph 1.
- **CTA**: Single, distinct button or hyperlink.

#### H. Social Media & Developer Announcements
- Respect character limits (X/Twitter: 280 chars; LinkedIn: first 150 chars visible before "see more").
- Hook in line 1; avoid opening with greetings like "Hey everyone!" or "We are thrilled to announce".
- Use bullet points for feature lists; provide a direct link to docs or demo.
- Limit hashtags to 1–3 relevant topic tags.

#### I. Storytelling in Tech (Case Studies & User Stories)
- **User Story**: `As a [Role], I want [Feature], so that [Business Benefit].`
- **Case Study Arc**:
  1. *Context*: The customer's architecture and traffic baseline.
  2. *Challenge*: The scaling bottleneck, incident, or developer productivity drain.
  3. *Exploration*: Why previous workarounds failed.
  4. *Implementation*: How the new solution integrated with their stack.
  5. *Quantified Results*: Percentage improvement in latency, cost reduction, or deployment frequency.

---

### Step 6: Tone, Voice, and Style Alignment

Adjust writing along four primary tone dimensions:

```
Formal  <----------------------------------------> Casual
Serious <----------------------------------------> Playful
Respectful <-------------------------------------> Irreverent
Matter-of-fact <---------------------------------> Enthusiastic
```

#### Style Guide Standards
- **AP Style**: Preferred for marketing copy, press releases, and general articles. Omits Oxford comma by default (unless required for ambiguity); numbers under 10 spelled out.
- **Chicago Manual of Style**: Preferred for books, deep-dive academic whitepapers, and formal documentation. Uses Oxford comma; numbers through one hundred spelled out.
- **Developer Style Guides (Google / Microsoft Developer Documentation)**:
  - Use sentence case for headings (`Install the command-line interface`, not `Install The Command-Line Interface`).
  - Use Oxford comma (`Python, Go, and Rust`).
  - Use contractions where natural (`don't`, `can't`) to maintain a conversational, approachable tone.
  - Spell out acronyms on first mention: `Virtual Private Cloud (VPC)`.

---

### Step 7: SEO and Technical Discoverability

- **Search Intent**: Match content format to user query type:
  - *Informational*: Tutorials, definitions, architectural guides.
  - *Navigational*: Reference docs, API spec sheets.
  - *Transactional / Commercial*: Pricing comparisons, migration tools, product overviews.
- **Keyword Placement**: Integrate target keyword in H1, first 100 words, one H2, and naturally in body text. Avoid keyword stuffing.
- **Meta Description**: 140–160 characters. Summarize the page value and include a reason to click.
- **Accessible Alt Text**: Describe the functional information conveyed in diagrams, charts, and screenshots:
  - *Weak*: `Screenshot of terminal`
  - *Strong*: `Terminal output showing successful database migration and 3 schema tables updated`

---

### Step 8: Localization (l10n) and Internationalization (i18n)

- **Avoid Idioms and Colloquialisms**: Phrases like "hit a home run", "under the hood", or "bite the bullet" do not translate cleanly.
- **Text Expansion**: Design UI microcopy knowing German, French, and Spanish translations may require 30–40% more space than English.
- **Date, Time, and Units**: Use unambiguous standards: ISO 8601 (`YYYY-MM-DD`), 24-hour time or explicit UTC offsets, and metric units.
- **Cultural Neutrality**: Avoid region-specific metaphors, sports references, or local political figures.

---

### Step 9: Editing and Proofreading Checklist

Run every draft through three distinct editing passes:

#### Pass 1: Structural & Substantive Edit
- [ ] Is the primary takeaway immediately obvious in the first paragraph?
- [ ] Are headings descriptive and logically ordered?
- [ ] Does each section contain only one major concept?
- [ ] Is there a clear next action or CTA at the end?

#### Pass 2: Line Edit (Style & Flow)
- [ ] Are sentences concise and under 25 words?
- [ ] Is the active voice used in over 85% of sentences?
- [ ] Have empty adjectives ("very", "really", "innovative", "seamless") been eliminated?
- [ ] Are transitions between paragraphs smooth?

#### Pass 3: Technical & Proofreading Edit
- [ ] Are code snippets tested, syntax-highlighted, and reproducible?
- [ ] Are CLI commands verified against latest release?
- [ ] Are links, anchor slugs, and cross-references working?
- [ ] Are capitalization, punctuation, and Oxford commas applied consistently?

---

## Best Practices

- **Show, Don't Tell**: Replace "Our engine is extremely fast" with "Our engine benchmarks at 1.2M queries per second on standard hardware."
- **One CTA per Context**: Presenting multiple conflicting actions (e.g., "Download Now", "Read Blog", "Follow Us") fragments attention and reduces conversion.
- **Write for Scanners**: Use bolding sparingly to emphasize key terms; use bulleted lists for collections of 3+ related items.
- **Assume Intelligence, Not Context**: Treat readers as capable engineers or thinkers who simply lack familiarity with your specific architecture, naming conventions, or assumptions.

---

## Common Pitfalls

- **The Curse of Knowledge**: Explaining a feature based on internal repository details rather than what the user needs to know.
- **Buried Ledes**: Hiding the most important instruction or outcome on page 3 beneath paragraphs of background history.
- **Blaming the User**: Using language like "You failed to supply the token" instead of "Session token required to connect."
- **Faux-Conversational Jargon**: Masking thin technical content behind hype words and exclamation marks.
- **Unverified Code Examples**: Publishing outdated snippets that fail due to missing dependencies, syntax errors, or deprecated APIs.

---

## Verification

To confirm the quality and readiness of written content, verify against these objective criteria:

1. **Readability Benchmark**:
   - Technical documentation: Flesch-Kincaid Grade Level 8–10.
   - UI microcopy & marketing landing pages: Flesch-Kincaid Grade Level 6–8.
   - Check with command line:
     ```bash
     # Install or run text statistics via style linters if available
     vale --version || echo "Install vale for automated style checking"
     ```
2. **Microcopy 4-Point Audit**:
   - Inspect every button, error, and tooltip. Does it identify the action, remove ambiguity, offer a resolution path, and maintain a calm tone?
3. **Runnable Code Test**:
   - Execute every code snippet in a clean shell or container to verify that instructions work as documented without hidden dependencies.
4. **Link & Anchor Slug Check**:
   - Ensure all internal Markdown links (`#section-name`) match actual header anchor slugs.
5. **Linting Rules**:
   - Run markdownlint or similar checkers:
     ```bash
     npx markdownlint-cli "**/*.md"
     ```
