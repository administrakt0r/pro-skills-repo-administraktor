#!/usr/bin/env python3
"""Apply an agent-authored, reviewed guideline plan. Never execute repository code.

Exit codes: 0 success/current, 1 preview or check found changes, 2 invalid/conflict/I/O.
Writes are atomic per file, with complete validation before the first write.
"""
import argparse
import difflib
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Running a preview must not create bytecode files in the installed skill.
sys.dont_write_bytecode = True

from upsert_section import (
    apply_upsert, atomic_write, compute_content_hash, find_marker_span, reject_symlinks,
)

MARKER = 'stack-guidelines'
MAX_PLAN_BYTES = 2 * 1024 * 1024
TARGET_NAME = re.compile(r'AGENTS(?:-GUIDELINES-[A-Z0-9-]+)?\.md')


def file_digest(content: Optional[bytes]) -> Optional[str]:
    return hashlib.sha256(content).hexdigest() if content is not None else None


def target_path(root: Path, name: str) -> Path:
    relative = Path(name)
    if relative.is_absolute() or not relative.parts or any(
        part in ('.', '..', '.git', 'node_modules', 'vendor') for part in relative.parts
    ) or not TARGET_NAME.fullmatch(relative.name):
        raise ValueError(f'Invalid guideline target: {name}')
    target = root / relative
    reject_symlinks(target)
    target.resolve().relative_to(root)
    if not target.parent.is_dir():
        raise ValueError(f'Guideline parent directory does not exist: {name}')
    return target


def prepare(root: Path, plan: Dict[str, Any], remove: bool = False) -> List[Tuple[Path, Optional[bytes], bytes]]:
    if not isinstance(plan, dict) or plan.get('schema_version') != 1:
        raise ValueError('Expected a schema_version: 1 plan object')
    entries = plan.get('files')
    if not isinstance(entries, list) or not entries or len(entries) > 200:
        raise ValueError('Plan files must contain between 1 and 200 entries')
    changes = []
    authored = {}
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get('path'), str):
            raise ValueError('Every file entry requires a string path')
        target = target_path(root, entry['path'])
        if target in seen:
            raise ValueError(f'Duplicate target: {entry["path"]}')
        seen.add(target)
        original = target.read_bytes() if target.exists() else None
        if 'expected_sha256' not in entry or entry['expected_sha256'] != file_digest(original):
            raise ValueError(f'Stale or missing expected_sha256: {entry["path"]}; reread and reconcile')
        content = entry.get('content', '')
        if not isinstance(content, str) or (not remove and not content.strip()):
            raise ValueError(f'Nonempty string content required: {entry["path"]}')
        if re.search(r'<!--\s*stack-guidelines:', content):
            raise ValueError('Plan content must not embed managed markers')
        existing = (original or b'').decode('utf-8')
        span = find_marker_span(existing, MARKER)
        if span and not re.search(r'\bhash=[a-f0-9]{8}\b', span[2]):
            raise ValueError(f'Unhashed legacy block: {entry["path"]}; reconcile manually before adoption')
        if target.name != 'AGENTS.md' and existing.strip() and not span:
            raise ValueError(f'Unmanaged guideline collision: {entry["path"]}')
        updated = apply_upsert(existing, content, MARKER,
                               meta={'skill': '2.0.0', 'hash': compute_content_hash(content)}, remove=remove)
        changes.append((target, original, updated.encode('utf-8')))
        authored[target] = content

    if not remove:
        proposed = {path: data for path, _, data in changes}
        # Check both markdown and backtick local instruction links.
        for path, content in authored.items():
            for name in re.findall(r'(?:`|\]\()((?:\./)?[^`\s()]*AGENTS(?:-GUIDELINES-[A-Z0-9-]+)?\.md)(?:`|\))', content):
                if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', name) or name.startswith('//'):
                    continue
                linked = path.parent / name
                reject_symlinks(linked)
                linked = linked.resolve()
                linked.relative_to(root)
                linked_data = proposed.get(linked)
                if linked_data is None:
                    linked_data = linked.read_bytes() if linked.is_file() else b''
                if not linked_data.strip():
                    raise ValueError(f'Missing or empty guideline link in {path.relative_to(root)}: {name}')
    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, help='Repository root')
    parser.add_argument('--plan', required=True, help='JSON plan with authored content and expected file hashes')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--dry-run', action='store_true', help='Show diffs without writing; 1 if changes')
    mode.add_argument('--check', action='store_true', help='List changed paths without writing; 1 if changes')
    parser.add_argument('--remove', action='store_true', help='Remove only the listed managed blocks; retain files')
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        raise ValueError('Root must be an existing directory')
    plan_path = Path(args.plan)
    if plan_path.stat().st_size > MAX_PLAN_BYTES:
        raise ValueError('Plan exceeds 2 MiB limit')
    plan = json.loads(plan_path.read_text(encoding='utf-8'))
    changes = prepare(root, plan, remove=args.remove)
    pending = [(p, old, new) for p, old, new in changes if (old or b'') != new]
    if args.dry_run or args.check:
        for path, original, updated in pending:
            name = path.relative_to(root).as_posix()
            if args.check:
                print(name)
            else:
                sys.stdout.writelines(difflib.unified_diff(
                    (original or b'').decode('utf-8').splitlines(keepends=True),
                    updated.decode('utf-8').splitlines(keepends=True),
                    fromfile='a/' + name, tofile='b/' + name))
        return 1 if pending else 0
    # Recheck every snapshot before committing any change to catch stale plans.
    for path, original, _ in changes:
        reject_symlinks(path)
        current = path.read_bytes() if path.exists() else None
        if current != original:
            raise ValueError(f'File changed during preflight: {path.relative_to(root)}')
    written = []
    try:
        for path, _, updated in pending:
            atomic_write(path, updated)
            written.append(path.relative_to(root).as_posix())
    except OSError:
        sys.stderr.write('Write failed; files already changed: ' + ', '.join(written) + '\n')
        raise
    print(json.dumps({'status': 'applied' if pending else 'current', 'changed_files': written}))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, UnicodeError) as error:
        sys.stderr.write(f'Error: {error}\n')
        sys.exit(2)
