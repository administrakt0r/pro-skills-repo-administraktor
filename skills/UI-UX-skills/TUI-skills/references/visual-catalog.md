# TUI Visual Catalog

Pure reference material for terminal visual elements. Scan, don't read.

## Box-Drawing Characters

### Light (standard TUI borders)
```text
┌───┬───┐    Corners: ┌ ┐ └ ┘
│   │   │    T-pieces: ├ ┤ ┬ ┴
├───┼───┤    Cross:    ┼
│   │   │    Lines:    ─ │
└───┴───┘
```
### Heavy (emphasis borders)
```text
┏━━━┳━━━┓    Corners: ┏ ┓ ┗ ┛
┃   ┃   ┃    T-pieces: ┣ ┫ ┳ ┻
┣━━━╋━━━┫    Cross:    ╋
┃   ┃   ┃    Lines:    ━ ┃
┗━━━┻━━━┛
```
### Double (classic DOS/Norton style)
```text
╔═══╦═══╗    Corners: ╔ ╗ ╚ ╝
║   ║   ║    T-pieces: ╠ ╣ ╦ ╩
╠═══╬═══╣    Cross:    ╬
║   ║   ║    Lines:    ═ ║
╚═══╩═══╝
```
### Rounded (modern, friendly)
```text
╭───┬───╮    Corners: ╭ ╮ ╰ ╯
│   │   │    (T-pieces, cross, lines
├───┼───┤     same as light set)
│   │   │
╰───┴───╯
```
### Mixed: Heavy Header + Light Body
```text
┏━━━━━━━━━━━━━━━━━━━━┓
┃  Panel Title        ┃
┡━━━━━━━━━━━━━━━━━━━━┩
│  Content here       │
│  using light lines  │
└─────────────────────┘
```
### When to Use Which
| Style             | Use Case                                           |
| ----------------- | --------------------------------------------------- |
| Light `─│`        | Default panel borders, dividers, tables             |
| Heavy `━┃`        | Active/focused panel, headers, emphasis             |
| Double `═║`       | Legacy/retro aesthetic, prominent sections          |
| Rounded `╭╯`      | Modern/friendly feel, cards, tooltips, buttons      |
| Mixed heavy+light | Focus indicator (heavy = active, light = inactive)  |
| No border         | Background layering sufficient, minimal aesthetic   |

---

## Clickable Element Recipes

Every recipe below needs a hover state and a pressed state distinct from its resting state, plus a distinct focus/selection ring if the element can also be keyboard-navigated. Use background tint for hover, a filled/inverted fill for press, and an accent-colored border or left-bar for focus — never rely on one signal alone.

### Buttons
```text
Resting:   ╭─────────────╮      Hover:  ╭─────────────╮      Pressed: ┌─────────────┐
           │   Confirm   │             │▓  Confirm  ▓│                │  Confirm    │
           ╰─────────────╯             ╰─────────────╯                └─────────────┘
                                  (bg tint fills the pill)      (inverted/filled = "down")

Primary (accent fill):     ╭─────────────╮
                            │██ Confirm ██│   ← solid accent background, not just colored text
                            ╰─────────────╯

Secondary (outline only):  ╭─────────────╮
                            │   Cancel    │   ← border only, no fill; still clickable
                            ╰─────────────╯

Disabled:                  ╭─────────────╮
                            │ ░░Confirm░░ │   ← dimmed fill + dimmed text, no hover state at all
                            ╰─────────────╯
```

### Tabs
```text
Inactive tabs sit flush; the active tab "lifts" by breaking the underline.

╭────────╮┌────────┐┌────────┐
│ Files  │|Search  │|Settings│
┴────────┴└────────┘└────────┘
  ▲ active: rounded top, no bottom border, connects to panel below
                │ inactive: square top, full border, sits "behind" the active tab

Hover on inactive tab: brighten border color only, do not change shape
Click target = full tab width/height, not just the label text
```

### Checkboxes / Toggles
```text
Unchecked:  ☐  Unchecked (hover): ▢  Checked: ☑  Checked (hover): ▣

Toggle switch (off):  ○──────    Toggle switch (on):  ──────●
                       ░░░░░░                          ▓▓▓▓▓▓
(track dims when off, fills with accent when on; knob position is the primary signal, color is secondary)
```

### List Rows (click-to-select)
```text
Resting:    tomcat-service          ● Running    120ms
Hover:     ▏tomcat-service          ● Running    120ms   ← left bar in muted accent, faint bg tint
Selected:  ▎tomcat-service          ● Running    120ms   ← thicker left bar in full accent color
Hover+Sel: ▎tomcat-service          ● Running    120ms   ← full accent bar + slightly lighter bg tint

Whole row is the click target, not just the name column.
```

### Scrollbars (draggable)
```text
Vertical track + thumb:      Horizontal track + thumb:
│░░░░░░░░│                   ░░░▓▓▓▓░░░░░░░░░░░░
│░░░░░░░░│                   ────────────────────
│▓▓▓▓░░░░│  ← thumb          Hover on thumb: brighten thumb fill
│▓▓▓▓░░░░│                   Drag: thumb follows cursor 1:1, track stays fixed
│░░░░░░░░│
Minimal alt (no track bg):   just the thumb glyph, e.g. ┃ in accent color over blank gutter
```

### Badges / Pills (status tags, non-interactive)
```text
 draft    in review    ● live    ✗ failed    3 pending
──────    ──────────   ───────   ────────    ─────────
(subtle bg fill, rounded ends via half-block ▐ ▌ if framework lacks true pill shapes)

▐ live ▌   ← half-block characters simulate rounded pill edges in plain-text renderers
```

### Menus / Context Menus (right-click or dropdown)
```text
╭──────────────────╮
│ Open        Enter │
│ Rename       F2   │
│ Delete       Del  │
├──────────────────┤
│ Copy path   ⌘C    │
╰──────────────────╯
Hover row: full-width bg tint, same treatment as list rows above.
Always show the keyboard shortcut alongside the mouse-clickable label.
```

---

## Block Elements

### Fractional Blocks (horizontal, left-to-right fill)
```text
▏ ▎ ▍ ▌ ▋ ▊ ▉ █
```
1/8 through 8/8 width. Use for sub-character precision in horizontal bar charts, and for hover/selection accent bars (see List Rows above).

### Fractional Blocks (vertical, bottom-to-top fill)
```text
▁ ▂ ▃ ▄ ▅ ▆ ▇ █
```
1/8 through 8/8 height. Use for sparklines and vertical bar charts.

### Shade Blocks
```text
░ Light shade (25%)
▒ Medium shade (50%)
▓ Dark shade (75%)
█ Full block (100%)
```
Use for density visualization, heatmaps, background patterns, and disabled/pressed button fills.

### Progress Bar Recipes
```text
Simple:     [████████░░░░░░] 57%
Gradient:   [█████▓▒░░░░░░░] 57%
Thin:       ━━━━━━━━╸━━━━━━ 57%
Braille:    ⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀ 57%
Minimal:    ■■■■■■□□□□□□ 57%
```

---

## Braille Patterns (U+2800-U+28FF)

Each braille character is a 2-column × 4-row dot grid, encoding 8 bits:
```text
Dot positions:    ⠁(1) ⠂(2) ⠄(3) ⡀(7)
                  ⠈(4) ⠐(5) ⠠(6) ⢀(8)
Combined: ⣿ = all dots    ⠀ = empty (blank braille)
```
Use for high-resolution terminal graphics. Each character cell provides 2×4 = 8 sub-pixels, enabling line charts, scatter plots, and pixel art at 2× horizontal and 4× vertical resolution.

### Sparkline with Braille
```text
Network: ⣀⣤⣶⣿⣶⣤⣀⣀⣤⣶⣿⣿⣶⣤  Peak: 1.2 MB/s
```

---

## Status Indicators

### Dots and Bullets
```text
●  Filled circle (active, online, enabled)
○  Empty circle (inactive, offline, disabled)
◉  Bullseye (selected, current)
◆  Filled diamond (important, pinned)
◇  Empty diamond (available, optional)
```
### Check and Cross
```text
✓  Check mark (success, done, yes)      ✔  Heavy check
✗  Ballot X (failure, error, no)        ✘  Heavy X
☐  Unchecked checkbox                   ☑  Checked checkbox
```
### Severity/Priority
```text
▲  Up triangle (increase, higher, expand)
▼  Down triangle (decrease, lower, collapse)
⚠  Warning sign
ℹ  Information
⬤  Large circle (status dot)
```
### Arrows
```text
Navigation:  ← → ↑ ↓    ⇐ ⇒ ⇑ ⇓
Triangles:   ◀ ▶ ▲ ▼    ◁ ▷ △ ▽
Pointers:    ► ◄         ‣
Powerline:   ▏            (thin separator)
```
### Mouse Cursor Hints (drawn by the app, not the terminal cursor)
```text
Hoverable border edge (resize):   ┊  or  ╎   (dashed, brighter than normal border on hover)
Draggable handle:                 ⣿  or  ⠿   (grip dots, e.g. for reordering list items)
Clickable-but-not-yet-hovered:    kept visually distinct from plain text only via
                                   border/shape (see Clickable Element Recipes) —
                                   don't invent a permanent glyph just to mean "clickable"
```

---

## Tree Drawing

### Standard Tree
```text
├── src/
│   ├── main.rs
│   ├── lib.rs
│   └── utils/
│       ├── config.rs
│       └── helpers.rs
├── tests/
│   └── integration.rs
└── Cargo.toml
```
Characters: `├── ` (branch), `└── ` (last branch), `│   ` (continuation), `    ` (spacing)

Clickable tree rows: whole row is the click target (label + indent), not just the folder icon; a hover tint should span the full row width even though the tree depth varies per row.

### Compact Tree (for narrow panels)
```text
├ src/
│ ├ main.rs
│ └ utils/
│   └ config.rs
└ Cargo.toml
```

---

## Table Formatting

### Standard Table
```text
┌──────┬────────┬───────┐
│ Name │ Status │ CPU % │
├──────┼────────┼───────┤
│ web  │ ● Run  │  23.4 │
│ db   │ ● Run  │   8.1 │
│ cache│ ○ Stop │   0.0 │
└──────┴────────┴───────┘
```
### Minimal Table (no outer border)
```text
 Name   Status   CPU %
 ─────  ──────   ─────
 web    ● Run     23.4
 db     ● Run      8.1
 cache  ○ Stop     0.0
```
### Zebra Stripe (alternating background)
Use `bg.surface` on even rows, `bg.base` on odd rows for scanability. If rows are clickable, hover/selection tint must still be visually distinguishable from the zebra stripe underneath it — test the darker stripe + hover combination specifically, since two subtle tints can cancel out.

### Sortable Column Headers (clickable)
```text
Name ▲     Status      CPU %      ← active sort column, arrow shows direction
Name       Status ▼    CPU %      ← hover on an inactive header: underline or brighten, no arrow yet
```

---

## Separator Styles
```text
Light:     ────────────────────────
Heavy:     ━━━━━━━━━━━━━━━━━━━━━━━━
Double:    ════════════════════════
Dashed:    ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
Dotted:    ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
Mixed:     ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
Labeled:   ──── Section Title ──────
```

---

## Diff Presentation

### Inline (unified)
```text
  fn process(data: &str) {     (context - default color)
-     let result = parse(data); (removed - red + dim)
+     let result = parse_v2(data); (added - green)
      result.validate()         (context - default color)
  }
```
### Side-by-Side
```text
│ fn process(data: &str) {     │ fn process(data: &str) {     │
│-  let result = parse(data);  │+  let result = parse_v2(data);│
│   result.validate()          │   result.validate()          │
```
Word-level diff highlighting within changed lines dramatically improves readability. Highlight the changed words/tokens, not just the whole line.

---

## Gauge Patterns
```text
CPU:  [████████████████████░░░░░░░░░░] 67%
Mem:  [███████████████░░░░░░░░░░░░░░░] 50%  8.0G/16.0G
Disk: [██████████████████████████████] 99%  ← red when >90%
Bat:  [████████░░░░░░░░░░░░░░░░░░░░░] 27%  ⚡ charging
```
Choose thresholds from the metric: high CPU utilization may be healthy while high disk usage may require action. Label the value and units so color is never the only signal.

---

## Common Nerd Font Icons

Use only with an explicit user setting or a known bundled font. No portable terminal query reliably establishes Nerd Font availability. Provide a Unicode/ASCII fallback.

| Meaning   | Unicode fallback | ASCII fallback |
| --------- | ----------------- | ---------------- |
| Directory | ▸                  | >                |
| File      | ·                  | *                |
| Success   | ✓                  | OK               |
| Error     | ✗                  | ERR              |
| Warning   | ⚠                  | !                |

**Rule:** Never assume Nerd Fonts are installed. Always define a fallback using standard Unicode or ASCII.

## Width and Accessibility

These glyphs are examples, not width guarantees. Use grapheme-aware truncation and the toolkit's cell-width handling; test wide text, combining marks, and emoji sequences. A braille chart needs a numeric summary or table when its pattern is not accessible. Pair status symbols with labels and offer ASCII where fonts or screen readers need it. Hover/press states built from background tint alone need a secondary cue (border, shape, or label change) for the same reason color-only status signals do.

Primary reference (checked 2026-09-04): [Unicode text segmentation](https://unicode.org/reports/tr29/). Terminal cell width is an additional rendering concern, not something grapheme segmentation alone decides.
