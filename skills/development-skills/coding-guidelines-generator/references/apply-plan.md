# Safe application of authored guidelines

The agent writes the content after inspecting the target repository. The helper
validates and applies that content; it does not synthesize rules or run project code.
It requires Python 3.8+ and the standard library.

## Plan format

Save a UTF-8 JSON object in a temporary location, outside tracked project files:

```json
{
  "schema_version": 1,
  "files": [
    {
      "path": "AGENTS-GUIDELINES-JS.md",
      "expected_sha256": null,
      "content": "# JavaScript guidelines\n\nScope: src/. Preserve the existing module format."
    },
    {
      "path": "AGENTS.md",
      "expected_sha256": null,
      "content": "## Stack guidelines\n\nRead `./AGENTS-GUIDELINES-JS.md` before editing src/."
    }
  ]
}
```

`path` is relative to the chosen repository root. Only `AGENTS.md` and
`AGENTS-GUIDELINES-<UPPERCASE-NAME>.md` are accepted. Parent directories must exist;
absolute paths, traversal, symlink targets/ancestors, and reserved dependency/Git
paths are rejected. Each target appears once. For an existing file,
`expected_sha256` is `hashlib.sha256(path.read_bytes()).hexdigest()` from the exact
bytes inspected. Use JSON null only when the file does not exist. A stale plan
must be rebuilt after rereading and reconciling current content.

`content` is the complete desired **inner managed block**, without marker comments.
It does not replace the whole existing file. Include missing baseline safeguards
and routing together in the AGENTS entry, without copying equivalent human text.
Guideline files can combine multiple reference layers or scoped package sections.
Any local instruction links must resolve to nonempty existing or planned files.
Do not embed secrets or unsupported "verified" claims in the plan.

## Lifecycle

Invoke scripts relative to the installed skill's directory, not the target repo:

```bash
python3 <skill-directory>/scripts/apply_guidelines.py --root <repository-root> --plan <plan.json> --dry-run
python3 <skill-directory>/scripts/apply_guidelines.py --root <repository-root> --plan <plan.json>
```

For verification, rebuild only the expected file hashes after applying; retain the
same desired content. `--check` then exits 0, and another apply is byte-identical.
`--dry-run` shows a diff; `--check` lists differing paths. Both remain read-only.
Exit codes: 0 successful/current; 1 changes in preview/check; 2 conflict or error.
A missing script/interpreter or unexpected stderr is a failure, not a successful
negative test.

For requested removal, list all owned files and their current hashes in a plan
then pass `--remove` (can combine with `--dry-run` or `--check`). Content is ignored.
Only managed blocks and recorded helper-added separators are removed. Files,
manual notes, and existing separators remain. Empty files are retained deliberately.
Remove or update the corresponding managed AGENTS routes in the same reviewed set.

## Ownership and recovery

The marker remains `stack-guidelines`; new blocks include `skill=2.0.0`, a content
hash, and padding metadata. The hash detects edits; it is not an authorization or
security signature. Malformed/duplicate markers, modified hashed blocks, unhashed
legacy blocks, and unmanaged guideline collisions stop application. Reconcile
legacy/manual content explicitly; do not delete a hash or marker to bypass a conflict.

Every target is validated before the first write. Each file replacement is atomic
and retains existing permissions. Multiple files are **not** one atomic transaction:
if an I/O failure occurs, the helper reports paths already written. Inspect the
actual state and regenerate the plan; do not claim that the whole set was rolled
back. Concurrent edits after preflight are not transactionally locked; avoid
simultaneous writers and recheck the final diff. No global force/overwrite mode exists.
