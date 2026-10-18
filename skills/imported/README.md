# Imported Skills

This directory contains external, high-value skills imported from verified
upstream open-source repositories and standards.

## Security & Verification Guarantee

Every skill in this directory has undergone a clean-room security and quality
audit via [`new-skill-import.md`](../../new-skill-import.md):
- **Scanned for prompt injection**: Verified clean of jailbreaks, instructions to
  ignore system constraints, and agent hijacking.
- **Scanned for malicious payloads**: No hidden Unicode zero-width characters,
  obfuscated code, unauthorized shell downloads, or data exfiltration.
- **Enhanced for quality**: APIs, CLI flags, and versions verified against
  current official documentation; broken examples repaired; missing `README.md`
  or structure added.
- **Provenance logged**: Original upstream source, author, license, and import
  date are recorded in [`new-skill-import-log.md`](../../new-skill-import-log.md).

## Organization

Imported skills are organized into categorized subdirectories:

```text
skills/imported/
├── <category-name>/
│   └── <skill-name>/
│       ├── SKILL.md
│       ├── README.md
│       └── references/
```

To import a new skill, run the procedure defined in
[`new-skill-import.md`](../../new-skill-import.md).
