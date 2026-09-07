# TUI Patterns Worth Borrowing

Use these applications as design references, not benchmark rankings or API documentation. Copy the interaction principle only when it serves the current task.

## Persistent Context: lazygit

A selector plus detail pane lets a user move among files, history, and changes while preserving a place to inspect the selected item. Context-sensitive actions reduce the need to memorize global shortcuts. The useful lesson is stable panel responsibility, not an exact panel count or a claim that every panel is always visible.

Use this shape for related resource lists. On narrow terminals, collapse secondary context and restore its selection when it returns. Avoid squeezing six panels into a viewport where no value is readable.

Mouse notes: lazygit ships with mouse events on by default — clicking a panel focuses it, clicking a row selects it, and dragging in a diff view creates a range selection. This is a real, shipped example of the click-to-focus and drag-to-select-range patterns described in the main skill. It also demonstrates the tradeoff those patterns carry: capturing clicks for UI focus can fight the terminal emulator's own text-selection/copy behavior, which is why lazygit exposes `gui.mouseEvents: false` and documents a modifier-key escape hatch (e.g. holding Option/Fn) for users who need native terminal selection back. Any TUI that captures mouse events for its own use should offer the same kind of opt-out.

Primary reference: [lazygit repository and feature demonstrations](https://github.com/jesseduffield/lazygit).

## Hierarchy and Preview: Yazi

Parent/current/preview columns keep location and consequence visible during navigation. Preview work may be slow, so the cursor must move independently of decoding or file I/O. Tag preview requests with the selected resource identity to prevent late results replacing the current preview.

Use columns for hierarchical exploration. Prefer a stack with back-navigation when width is limited. Preserve the user's selection and scrolling per location instead of resetting every visit to the first row.

Primary reference: [Yazi layout and preview configuration](https://yazi-rs.github.io/docs/configuration/yazi/).

## Direct Focus: Posting

A multi-panel HTTP client benefits from a way to focus a distant control without cycling through every field. Posting's jump mode demonstrates visible target labels; a command palette can provide a complementary action route.

Use direct-focus labels when the screen has many interactive targets. Keep ordinary Tab navigation and ensure printable input belongs to the editor while it is focused. Labels should follow the visible layout and must not survive after their target disappears.

Primary reference: [Posting guide](https://posting.sh/guide/).

## Live Data: Dashboard and Log Patterns

A dashboard needs stable units, update freshness, and an explicit distinction between unavailable and zero. A log viewer needs a stable viewport, follow/pause behavior, and searchable retained events. Decorative activity is not evidence that the underlying request or stream remains healthy.

For high data rates, virtualize rows and separate storage from presentation. Keep selected item identity stable as sorting changes. If a paused view has new data, show the count or time boundary instead of dragging the user back to the end.

## Shell Integration: Picker Pattern

An inline picker should return one well-defined result to its caller and send interactive chrome to the appropriate terminal stream. Cancellation must differ from selecting an empty value. Restore terminal state before the shell consumes the result, and preserve scrollback where the chosen presentation allows it.

## Mouse Support in Practice: Three Valid Stances

Real, widely-used TUIs disagree on how much mouse support to build, and all three positions are defensible — pick deliberately rather than by default.

- **On by default, with an escape hatch (lazygit).** Click-to-focus, click-to-select, and drag-to-range-select are all live. This is the richest mouse experience of the three, but it's also the one most likely to collide with the terminal's own text selection — hence the documented opt-out above. Choose this stance when the app's primary users will treat it like a visual tool first and a terminal tool second.
- **Off by default, opt-in (k9s).** `k9s` ships `ui.enableMouse: false` and documents flipping it on for click-to-select in resource lists. This keeps the default experience identical to the keyboard-only tradition its users expect, while still giving mouse-preferring users a path in. Choose this stance when the existing user base is keyboard-first and you don't want to change default behavior underfoot.
- **Deliberately not a focus (gitui).** The maintainers have stated mouse support isn't a priority, citing a philosophy of keyboard-first speed, though they've said they wouldn't block a community-contributed patch. This is a legitimate stance, not neglect — some tools are genuinely better served by staying keyboard-only and investing that effort in shortcut ergonomics instead.

The lesson isn't "always add mouse support" — it's that the three real precedents above map cleanly onto the main skill's `Make It Feel Modern and Clickable` guidance: decide the stance intentionally, and if you do add mouse support, decide up front whether it's on-by-default or opt-in, and always keep a way to get native terminal text selection back.

## Compose Only What the Task Needs

| User need            | Start with                               | Add only when justified                     |
| --------------------- | ------------------------------------------ | ---------------------------------------------- |
| Choose one value     | List, filter, preview                    | Multi-select, saved searches                |
| Explore a hierarchy  | Stack or columns                         | Bookmarks, multiple independent panes       |
| Edit structured data | Editor plus validation/result view       | Tabs, jump labels, command palette          |
| Operate resources    | Selector, details, explicit action state | Batch operations with a reviewed target set |
| Monitor events       | List, filter, follow state               | Charts or correlated detail views           |
| Click-driven browsing | Keyboard-complete navigation first       | Mouse support, chosen as on-by-default or opt-in (see above), never mouse-only |

The recommendations above are design synthesis. Source behavior was checked 2026-09-07; revisit the application docs for current keybindings and configuration syntax.
