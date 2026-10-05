---
name: content-marketing
description: >-
  Plan, produce, optimize, distribute, and measure high-impact content marketing campaigns across technical blogs, landing pages, email sequences, social platforms, developer communities, and open source repositories. Use when creating content strategies, writing technical blog posts or launch announcements, optimizing copy for conversions and SEO, planning content calendars, building developer relations and open source marketing collateral, repurposing assets across channels, executing outreach and distribution, or establishing analytics and A/B testing frameworks.
---

# Content Marketing

Content marketing is a systematic discipline that builds trust, drives organic acquisition, and converts qualified audiences into engaged users, contributors, and paying customers through high-value technical and narrative material. In technical and developer-focused ecosystems, content marketing prioritizes substance over fluff: providing concrete code examples, verifiable benchmarks, architectural trade-offs, and actionable problem solving.

This skill equips agents to plan, produce, distribute, and measure content across all channels—from technical blog posts and landing pages to email newsletters, social distribution, developer relations (DevRel), and open source repository positioning.

---

## When to Use

Activate this skill when:
- Defining content strategies, target personas (ICPs), and channel distribution plans.
- Writing or refactoring technical blog posts, tutorials, release announcements, case studies, or comparison articles.
- Writing high-converting landing page copy, value propositions, and social proof elements.
- Planning and composing social media posts or threads (Twitter/X, LinkedIn, Reddit, Product Hunt, Hacker News).
- Designing email marketing campaigns, automated onboarding drip sequences, and newsletters.
- Establishing content calendar schedules, editorial review pipelines, and keyword-to-content SEO architectures.
- Launching and positioning open source projects (README marketing, badges, topics, and community engagement).
- Repurposing cornerstone content into social threads, newsletters, video/demo walkthrough scripts, and documentation.
- Setting up content analytics, UTM tracking conventions, conversion funnels, and A/B copy tests.
- Formulating developer outreach, link-building initiatives, and community activation strategies (Discord, GitHub Discussions).

---

## Prerequisites

- Markdown editor or static site generator (e.g., Hugo, Astro, Next.js, Starlight, Docusaurus).
- Basic CLI tools for link verification and content linting (`vale`, `markdownlint`, `lychee`, or `curl`).
- Web search / keyword discovery tools (Google Search Console, Ahrefs, Semrush, or open search operators).
- Web analytics instrumentation (Plausible, PostHog, Google Analytics 4, or Fathom).
- Git for version-controlled content workflows and branch-based editorial review.

---

## Steps

### Step 1: Define Strategy, Audience, and Channel-Goal Fit

Every piece of content must solve a specific problem for an explicitly defined audience segment. Avoid generic "thought leadership" that addresses no one in particular.

#### 1. Define Ideal Customer Persona (ICP) & Developer Archetypes
Map content to one of three primary reader archetypes:

| Dimension | Practicing Developer / Practitioner | Engineering Leader / Architect | Founder / Executive Buyer |
| :--- | :--- | :--- | :--- |
| **Primary Need** | "How do I fix this error right now?" | "Will this scale securely without tech debt?" | "What is the ROI and time-to-market impact?" |
| **Tone & Style** | Direct, code-rich, minimal adjectives | Evaluative, architectural diagrams, trade-offs | Outcome-focused, business metrics, risk mitigation |
| **Key Validation** | Copy-pasteable snippet that works | Benchmark charts, migration guides | Customer case studies, logos, security posture |

#### 2. Establish Content Goals & Funnel Mapping
Classify every asset into the marketing funnel:
- **Top of Funnel (ToFu - Awareness):** Solves common engineering pain points, explains concepts, or covers industry shifts (e.g., *"Understanding Distributed Lock Contention in PostgreSQL"*).
- **Middle of Funnel (MoFu - Evaluation):** Compares solutions, breaks down architecture, and showcases product capabilities without hard-selling (e.g., *"Redis vs. Memcached vs. OurEngine for Distributed Caching"*).
- **Bottom of Funnel (BoFu - Conversion):** Migration guides, ROI teardowns, detailed implementation blueprints (e.g., *"Migrating from Tool A to OurEngine in 30 Minutes"*).

---

### Step 2: Conduct Keyword Research and Structure Content-SEO Alignment

Target search intent directly rather than stuffing keywords. Match the structure to how both humans and search engines parse information.

#### 1. Search Intent Classification
Identify user intent before writing:
- **Informational:** Queries starting with "how to", "what is", "best practices for". Format: Step-by-step tutorial or architectural breakdown.
- **Commercial Investigation:** Queries with "vs", "alternatives to", "pricing", "review". Format: Unbiased comparison table, feature matrix, benchmark charts.
- **Transactional:** Queries with "download", "install", "template", "API client". Format: Quickstart landing page with copy-paste commands.

#### 2. Frontmatter and Technical Meta Schema
Equip every markdown article with semantic, SEO-optimized metadata:

```markdown
---
title: "Mastering Database Connection Pooling: Architecture and Benchmarks"
description: "Learn how to optimize database connection pools, eliminate connection exhaustion, and benchmark throughput across high-concurrency workloads."
slug: "mastering-database-connection-pooling"
publishDate: "2026-10-06"
authors: ["engineering-team"]
tags: ["databases", "performance", "backend", "architecture"]
canonicalUrl: "https://example.com/blog/mastering-database-connection-pooling"
openGraph:
  title: "Mastering Database Connection Pooling: Architecture and Benchmarks"
  description: "Eliminate connection exhaustion and boost backend throughput. Full benchmarks inside."
  image: "https://example.com/images/og-connection-pooling.png"
  type: "article"
twitter:
  card: "summary_large_image"
  site: "@exampleorg"
---
```

#### 3. Pillar-and-Cluster Model
Organize related topics into hub-and-spoke architectures:
- **Pillar Page:** Broad, comprehensive guide (e.g., `/guides/api-security-handbook`).
- **Cluster Pages:** Specialized deep-dives that link back to the pillar (e.g., `/blog/jwt-validation-best-practices`, `/blog/rate-limiting-algorithms`, `/blog/oauth2-pkce-flow`).
- Maintain bidirectional internal links: every cluster links back to the pillar within the first two paragraphs; the pillar links to all cluster deep-dives.

---

### Step 3: Write High-Retention Technical Blog Posts

Technical readers detect superficial content immediately. Structure posts to deliver immediate value before expanding into technical depth.

#### 1. The Hook Framework (The First 150 Words)
Open with a three-part hook:
1. **The Friction (Pain Point):** A concrete, relatable problem or failure scenario.
2. **The Stakes:** Why common workarounds fail or cost time/money.
3. **The Solution:** What this article delivers, including code, benchmark results, and production-tested patterns.

*Example Hook:*
> When microservice traffic spikes by 10x, standard database connection setups collapse in a cascade of `504 Gateway Timeout` errors. Increasing `max_connections` usually shifts the bottleneck to CPU saturation and memory starvation. In this guide, we break down connection pool sizing formulas, implement adaptive pool sizing in Go, and benchmark the results under 50,000 requests per second.

#### 2. Readability & Structure Best Practices
- **F-Pattern Layout:** Use bold key terms in the first 3–5 words of paragraphs.
- **Scannable Hierarchy:** Only one `H1`. Use `H2` for primary chapters, `H3` for distinct technical steps.
- **Code Snippets:** Provide complete, runnable code blocks with language identifiers. Avoid truncated snippets with missing imports or invisible prerequisites.
- **Visual Pauses:** Insert an architectural diagram (Mermaid or SVG), benchmark table, or callout box every 300–400 words.

#### 3. Strategic Call-to-Action (CTA) Placement
Deploy three tiers of CTAs without interrupting reading flow:
- **Top / Sticky Banner (Passive):** Brief link to related open source repo or docs.
- **Mid-Article Contextual CTA:** In-line link to a downloadable tool, repo starter, or sandbox relevant to the current section.
- **Terminal CTA (Active):** A clear, low-friction next step at the bottom of the article:

```markdown
---
### Try It Yourself

Clone the benchmark repository and reproduce these numbers on your local machine:

```bash
git clone https://github.com/example/connection-pool-benchmarks.git
cd connection-pool-benchmarks && make run
```

If you found this useful, star the project on GitHub or join our community Discord to discuss distributed systems architectures.
---
```

---

### Step 4: Craft High-Converting Landing Page Copy

Landing pages exist to clarify value and eliminate friction. Structure pages around the **Hero $\rightarrow$ Problem $\rightarrow$ Solution $\rightarrow$ Social Proof $\rightarrow$ Objection Handling $\rightarrow$ Action** sequence.

#### 1. Above-the-Fold Hero Section Formula
- **Superhead (Category Identifier):** 2–4 words specifying the category (e.g., `OPEN SOURCE DISTRIBUTED CACHE`).
- **Headline (The Primary Promise):** Clear over clever. State the specific outcome (e.g., *"Sub-Millisecond Query Caching for Modern PostgreSQL Stacks"*).
- **Subheadline (The Mechanism & Audience):** 1–2 sentences clarifying who it is for, how it works, and what it replaces (e.g., *"Drop-in caching layer that auto-invalidates on write. Zero schema changes required. Built for high-throughput Go and Node.js backends."*).
- **Primary CTA + Secondary CTA:** Low-commitment primary action (`Get Started in 60s` / `Copy CLI command`) + risk-free secondary action (`Explore Interactive Demo` / `View on GitHub ⭐ 8.4k`).
- **Social Proof / Trust Badge:** Micro-copy directly beneath CTA (`No credit card required • MIT Licensed • Self-hostable`).

#### 2. Value Proposition Grid
Present features as *Capabilities $\rightarrow$ Outcomes*, not dry specifications:

```markdown
| Capability | Technical Mechanism | Tangible Outcome |
| :--- | :--- | :--- |
| **Instant Cache Invalidation** | Real-time WAL log replication | Zero stale reads across distributed replicas |
| **Zero Infrastructure Sprawl** | Single statically-linked binary | Runs in 35MB RAM without Docker dependencies |
| **Automatic Schema Introspection** | AST parser for incoming SQL | Drop-in acceleration with zero code rewrites |
```

#### 3. Objection Handling & FAQ Accordion
Address security, compliance, performance, and vendor lock-in directly on the page:
- *"Does this require sending our data to third-party servers?"* (Highlight self-hosted and on-prem capabilities).
- *"What happens if the service goes down?"* (Detail fail-open architecture and circuit-breaking).
- *"How difficult is migration?"* (Highlight backward compatibility and single-line SDK swaps).

---

### Step 5: Engineer Platform-Specific Social Media Distribution

Never cross-post the exact same message across social platforms. Adapt format, syntax, and cultural norms per network.

#### 1. Twitter / X Technical Threads
- **Tweet 1 (Hook):** State an unintuitive finding, architectural breakdown, or benchmark result. Include a high-res chart, code snippet, or diagram.
- **Tweets 2–6 (Body):** One key insight or step per tweet. Use numbered bullets and code snippets.
- **Tweet 7 (Takeaway):** Concise summary checklist.
- **Tweet 8 (CTA & Link):** Link to the long-form article, repo, or documentation. (Avoid external links in Tweet 1 to prevent algorithmic reach penalties).

#### 2. LinkedIn Engineering & Leadership Posts
- **Tone:** Professional, reflective, architectural, and culture-aware.
- **Formatting:** Short 1–2 line paragraphs with white space. Avoid hashtag stuffing (limit to 3 relevant tags at the end).
- **Focus:** Technical leadership decisions, post-mortems, scaling challenges, or lessons learned during development.

#### 3. Reddit Technical Communities (r/programming, r/devops, r/webdev)
- **Golden Rule:** Value first, self-promotion secondary or non-existent.
- **Format:** Submit as a **Text Post (Self-Post)**, not a bare external link.
- **Content:** Transcribe the core engineering insights, architecture decisions, and code directly into the Reddit post body.
- **Disclosure:** Conclude with transparent attribution: *"Full benchmarks and repo source are linked here if anyone wants to inspect the raw data: [link]. Feedback and criticism welcome."*

#### 4. Product Hunt Launch Protocol
- **Tagline (60 chars):** Specific outcome + audience (e.g., *"Open-source database caching with zero code changes"*).
- **First Maker Comment:** Written within 2 minutes of launch. Explain:
  1. Why you built it (the origin story and personal frustration).
  2. The core technical architecture and trade-offs made.
  3. What is free/open source vs. commercial (if applicable).
  4. Special perks or invitations for the community.
- **Visual Assets:** 1280x720 video walkthrough or animated GIFs showcasing the product functioning in real-time within the first 5 seconds.

---

### Step 6: Construct Email Sequences and Newsletters

Email represents direct, owned audience communication unmediated by third-party algorithms.

#### 1. Automated Onboarding / Drip Sequence Architecture
Design a 5-part email sequence for new signups or documentation downloads:

```
Day 0: Welcome & Immediate Value
  └── Deliver requested resource + 60-second quickstart snippet.
Day 2: The Core "Aha!" Moment
  └── Walk through the single most powerful feature with a concrete code sample.
Day 5: Deep-Dive Architecture / Production Readiness
  └── How to configure production resilience, security, or monitoring.
Day 9: Case Study / Community Spotlight
  └── Real-world benchmark or customer story overcoming a scaling barrier.
Day 14: Conversion / Community Invitation
  └── Direct invitation to join community Discord, schedule demo, or upgrade.
```

#### 2. Subject Line Engineering
- **High-performing patterns:**
  - *Curiosity + Specificity:* "Why Redis memory usage spikes after 100k keys (and how to fix it)"
  - *Data / Benchmark Driven:* "We cut API latency from 240ms to 18ms. Here is the diff."
  - *Direct Utility:* "Cheat sheet: 12 PostgreSQL indexing rules for production"
- **Rules:** Keep subject lines under 50 characters. Use preview text (preheader) to extend the sentence rather than duplicating it. Avoid spam triggers: all-caps words, excessive punctuation (`???`), or deceptive prefixes (`Re:`, `Fwd:`).

#### 3. Segmentation Taxonomy
Segment subscribers based on behavior and technical role:
- `role:practitioner` vs. `role:leader` vs. `role:founder`
- `status:free_user` vs. `status:paid_customer` vs. `status:open_source_contributor`
- `activity:active_30d` vs. `activity:dormant_60d` (target dormant users with win-back sequences before pruning).

---

### Step 7: Market Open Source Projects and Drive Developer Relations (DevRel)

In developer marketing, the repository is the primary conversion landing page. Treat the `README.md` as a sales page written for engineers.

#### 1. High-Converting README Structure
Ensure repository root files follow this sequence:
1. **Header Banner & Shields:** Logo, concise tagline, and verifiable badges (License, CI build, latest release, Discord/Community link).
2. **Problem Statement:** 2–3 sentences stating the exact pain point solved.
3. **Quickstart (First 60 Seconds):** Single copy-pasteable installation and run block.
4. **Feature Highlights:** 3–5 bullet points highlighting concrete capabilities.
5. **Architecture / How It Works:** Clean diagram showing data flow or components.
6. **Comparison Matrix:** Objective trade-off table against alternatives.
7. **Contributing & Community:** Clear contributing guide link and community channels.

#### 2. GitHub Topics and Repository SEO
Configure repository settings for discoverability:
- Set 10–15 relevant GitHub topics: e.g., `caching`, `database`, `postgresql`, `developer-tools`, `high-performance`, `golang`.
- Fill the repository description with core keywords.
- Set the Social Preview Image (`1280x640px`) with high-contrast text and branding.

#### 3. Developer Documentation as Marketing
- Documentation ranks higher than marketing blog posts for high-intent technical search queries.
- Include "recipes", "quickstarts", and copy-paste boilerplate templates in docs.
- Provide interactive code playgrounds or embedded sandboxes (CodeSandbox, StackBlitz, or WebAssembly demos) whenever technically possible.

---

### Step 8: Build the 1-to-10 Content Repurposing Engine

Never write a cornerstone piece of content for a single channel. Every in-depth article should produce a cascade of derived assets:

```
Cornerstone Technical Article (2,500 words)
 │
 ├── 1. Twitter/X Hook Thread (8-10 tweets focusing on core architectural insight)
 ├── 2. LinkedIn Post (Executive summary focusing on engineering team lessons learned)
 ├── 3. Reddit Self-Post (Unrolled markdown technical guide for r/programming)
 ├── 4. Product Newsletter Edition (Curated takeaways with code link)
 ├── 5. Video / Demo Walkthrough Script (3-5 minute screen recording outline)
 ├── 6. GitHub Discussion / Community Topic (Prompting technical debate)
 └── 7. Documentation Snippet / Recipe (Integrated into permanent docs site)
```

---

### Step 9: Content Distribution, Outreach, and Link Building

Publishing is only 30% of the workflow; distribution accounts for the remaining 70%.

#### 1. The Owned, Earned, and Shared Distribution Checklist
Upon publishing, execute distribution across three tiers:
- **Owned Channels:** RSS feed, email newsletter, product changelog, documentation updates.
- **Shared / Community Channels:** Official Discord/Slack announcements, Twitter/X, LinkedIn, Mastodon/Bluesky.
- **Earned / Aggregator Channels:**
  - Submit to Hacker News (`Show HN` if a product/tool, standard link if high-depth technical article).
  - Submit to niche developer newsletters (e.g., JavaScript Weekly, Golang Weekly, DB Weekly, DevOps Weekly, TLDR).
  - Cross-post to developer platforms (Dev.to, Hashnode, Medium) with explicit `canonical_url` tags pointing to the original site.

#### 2. Cold Outreach for Newsletter Inclusion & Backlinks
When pitching newsletter curators or engineering bloggers, provide immediate value with zero fluff:

```text
Subject: Contribution for [Newsletter Name]: Database pool exhaustion deep-dive

Hi [Name],

I saw your recent issue covering Postgres query optimization. 

We just published a technical breakdown benchmarked across 50k req/sec showing how connection pooling exhaustion happens under microservice bursts, including an open source repro script:
[Link to article/repo]

Key takeaways your readers might find useful:
- Sizing formula: connections = ((core_count * 2) + effective_spindle_count)
- Benchmark data comparing static vs. adaptive pool sizing
- Zero-dependency Go implementation

If this aligns with what your subscribers look for, feel free to share it. Either way, appreciate your work on [Newsletter Name].

Best,
[Your Name]
```

---

### Step 10: Cultivate Developer Communities (Discord, GitHub Discussions)

Build an active community loop that turns users into contributors and advocates.

#### 1. The Community Flywheel
1. **Acquisition:** Users discover project via blog, GitHub, or social media.
2. **Onboarding:** Automated welcome channel or bot directing them to the `#getting-started` or `#showcase` channel.
3. **Value Realization:** Real-time help provided in public channels (creates indexed, searchable solutions).
4. **Contribution:** Users submit bug reports, docs improvements, or feature PRs.
5. **Advocacy:** Contributors are highlighted publicly (e.g., in release notes, social shoutouts), encouraging further participation.

#### 2. Channel Architecture
Keep developer communities lean. Start with at most 5 core channels:
- `#announcements` (Read-only releases and major updates)
- `#general` (Casual discussion and project philosophy)
- `#troubleshooting` or `#help` (Community support and technical questions)
- `#showcase` (Users sharing what they built with the tool)
- `#contributors` (Discussions around open pull requests and roadmap)

---

### Step 11: Establish Content Calendars and Editorial Pipelines

Maintain consistency by managing content production like software development: version-controlled, reviewed, and scheduled.

#### 1. Markdown Content Directory Organization
Structure content within the repository:

```text
content/
├── blog/
│   ├── 2026-10-06-database-connection-pooling/
│   │   ├── index.md
│   │   ├── benchmark-chart.svg
│   │   └── pool-architecture.png
│   └── 2026-10-14-understanding-wal-replication/
│       └── index.md
├── changelog/
│   └── v2.4.0.md
└── guides/
    └── high-availability-setup.md
```

#### 2. Production Cadence Matrix
- **Weekly:** 1 tactical technical blog post or deep-dive guide + 1 product changelog/release note.
- **Bi-Weekly:** 1 curated newsletter issue.
- **Daily / 3x Weekly:** Social distribution (threads, insights, engineering commentary).
- **Monthly:** 1 comprehensive pillar piece, major benchmark report, or case study.

---

### Step 12: Analytics, A/B Testing, and Performance Measurement

Measure content performance with clear attribution and quantitative metrics.

#### 1. Standardized UTM Taxonomy
Never share raw links on external channels. Enforce a standardized UTM convention:

```text
https://example.com/blog/connection-pooling?utm_source=twitter&utm_medium=social&utm_campaign=launch_v2&utm_content=thread_hook
```

| Parameter | Allowed Values / Standard | Example |
| :--- | :--- | :--- |
| `utm_source` | Platform name in lowercase | `twitter`, `linkedin`, `reddit`, `hackernews`, `newsletter` |
| `utm_medium` | Channel type | `social`, `email`, `cpc`, `referral`, `syndication` |
| `utm_campaign` | Specific campaign, release, or theme | `launch_v2`, `q4_developer_guide`, `benchmark_series` |
| `utm_content` | Specific asset variant or placement | `header_cta`, `terminal_cta`, `thread_tweet1`, `banner_a` |

#### 2. Key Content Metrics & North Star KPIs
Track metrics across three operational layers:

```markdown
1. Consumption & Reach:
   - Unique Visitors (UV) / Pageviews
   - Organic Search Clicks & Average Ranking Position (Google Search Console)
   - Social Impressions and Reposts

2. Engagement & Quality:
   - Median Scroll Depth (Target: >65% for long-form)
   - Average Time on Page (Target: >2.5 minutes for technical articles)
   - Code Snippet Copy Rate (Click event on `copy-code-button`)

3. Conversion & Business Impact:
   - Documentation / Quickstart Clicks
   - CLI Install Command Copies
   - GitHub Stars / Forks Generated
   - Newsletter Signups / Demo Requests
```

#### 3. A/B Testing Content Elements
When testing headlines, CTAs, or landing page layouts:
- **Test One Variable at a Time:** Test Headline A vs. Headline B while keeping body copy, graphics, and CTAs identical.
- **Sample Size & Statistical Significance:** Run tests until reaching at least 95% statistical confidence ($\ge 500$ conversions per variant for micro-actions, or $\ge 100$ for macro-actions).
- **Hypothesis-Driven:** Formulate clear test statements: *"Changing the CTA button text from 'Sign Up' to 'Copy Install Command' will increase developer activation rate because it eliminates account creation friction."*

---

## Best Practices

- **Show, Don't Tell:** In technical marketing, an annotated code block, reproducible terminal command, or architecture diagram is worth ten paragraphs of marketing prose.
- **Benchmark Honestly:** When comparing against alternatives, publish the exact hardware specifications, configuration files, and benchmark scripts. Unbiased transparency builds lasting technical credibility.
- **Honor Canonical URLs:** Always set `rel="canonical"` when syndicating to Dev.to, Medium, or Hashnode to prevent duplicate content search penalties.
- **Maintain Evergreen Content:** Review top-performing articles quarterly. Update outdated commands, dependencies, and version numbers to maintain search engine authority.
- **Respect Developer Communities:** Never astroturf or post automated promotional links on Hacker News, Reddit, or Discord. Engage authentically as an engineer building tools for engineers.

---

## Common Pitfalls

- **The "Bland Corporate Voice":** Writing buzzword-laden corporate copy ("leveraging scalable synergies") that developer audiences immediately dismiss.
- **The Missing Quickstart:** Forcing readers to read 2,000 words before showing them how to install, run, or test the tool.
- **Broken / Non-Reproducible Code:** Publishing code snippets with missing dependencies, unhandled errors, or obsolete APIs. Every code block must be tested.
- **Neglecting Distribution:** Spending 20 hours writing an article and only tweeting a single link once, resulting in zero initial momentum.
- **Ignoring Search Intent:** Writing a tutorial when searchers wanted a comparison table, or writing a sales pitch when searchers wanted a quick error fix.
- **Vanity Metric Obsession:** Celebrating millions of low-quality impressions while ignoring zero documentation clicks, zero signups, and zero community growth.

---

## Verification

To verify that content marketing assets meet production standards:

1. **Editorial Quality & Linting:**
   ```bash
   # Run automated spelling, prose, and style checking
   vale content/blog/
   markdownlint content/blog/
   ```

2. **Link Health & Asset Verification:**
   ```bash
   # Verify all internal and external hyperlinks are active and non-broken
   lychee "content/**/*.md" --exclude-mail
   ```

3. **SEO & Metadata Integrity:**
   - Confirm every markdown file includes `title`, `description`, `canonicalUrl`, and `openGraph` image.
   - Confirm title length is between 50–60 characters and description is between 140–160 characters.
   - Verify that code blocks specify valid language identifiers (e.g., ```` ```typescript ````, ```` ```bash ````).

4. **Tracking & Attribution:**
   - Verify all promotional outbound links include valid `utm_source`, `utm_medium`, and `utm_campaign` parameters.
   - Test landing page CTA event triggers in analytics real-time debuggers before launching traffic campaigns.

---

## Reference Material

For full copy templates, post blueprints, launch checklists, audit rubrics, and dashboard schemas, consult the companion guide:
- [`references/marketing-strategies.md`](references/marketing-strategies.md)
