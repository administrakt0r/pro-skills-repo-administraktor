#!/usr/bin/env python3
"""
upsert_section.py - Deterministic marker-based content upsert for AGENTS.md and guideline files.

Safely inserts or updates managed sections enclosed between marker comments:
    <!-- <marker-id>:start [metadata] -->
    ... managed content ...
    <!-- <marker-id>:end -->

Preserves all user content outside markers byte-for-byte. Idempotent across multiple runs.
Supports template placeholder substitution (--substitute KEY=VAL).
"""

import argparse
import difflib
import hashlib
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def compute_content_hash(text: str) -> str:
    """Compute an 8-character hex sha256 digest of normalized text."""
    normalized = text.strip().encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()[:8]


def build_markers(marker_id: str, meta: Optional[Dict[str, str]] = None) -> Tuple[str, str]:
    """Construct start and end markers with optional key=value metadata."""
    if meta:
        meta_str = " " + " ".join(f"{k}={v}" for k, v in meta.items())
    else:
        meta_str = ""

    start_marker = f"<!-- {marker_id}:start{meta_str} -->"
    end_marker = f"<!-- {marker_id}:end -->"
    return start_marker, end_marker


def find_marker_span(content: str, marker_id: str) -> Optional[Tuple[int, int, str, str]]:
    """
    Find existing marker span in content.
    Returns (start_idx, end_idx, start_marker_str, end_marker_str) or None.
    """
    start_pattern = rf"<!--\s*{re.escape(marker_id)}:start(\s+[^>]*)?\s*-->"
    end_pattern = rf"<!--\s*{re.escape(marker_id)}:end\s*-->"

    start_match = re.search(start_pattern, content)
    if not start_match:
        return None

    end_match = re.search(end_pattern, content[start_match.end():])
    if not end_match:
        return None

    actual_end_idx = start_match.end() + end_match.end()
    return (start_match.start(), actual_end_idx, start_match.group(0), end_match.group(0))


def apply_upsert(
    existing_content: str,
    new_inner_content: str,
    marker_id: str,
    position: str = "bottom",
    meta: Optional[Dict[str, str]] = None,
    remove: bool = False
) -> str:
    """
    Apply the upsert transformation to content string.
    Guarantees 100% byte-for-byte preservation of user content outside markers.
    """
    span = find_marker_span(existing_content, marker_id)
    start_marker, end_marker = build_markers(marker_id, meta)

    clean_inner = new_inner_content.strip()
    if clean_inner:
        block = f"{start_marker}\n{clean_inner}\n{end_marker}"
    else:
        block = f"{start_marker}\n{end_marker}"

    if remove:
        if not span:
            return existing_content
        start_idx, end_idx, _, _ = span
        before = existing_content[:start_idx]
        after = existing_content[end_idx:]

        # Clean only the boundary separator between before and after
        if before.endswith("\n\n") and after.startswith("\n"):
            after = after[1:]
        elif not before and after.startswith("\n"):
            after = after.lstrip("\n")
        elif before and not after and before.endswith("\n\n"):
            before = before[:-1]

        return f"{before}{after}"

    if span:
        start_idx, end_idx, _, _ = span
        before = existing_content[:start_idx]
        after = existing_content[end_idx:]
        return f"{before}{block}{after}"
    else:
        # Markers not present in existing content
        if not existing_content:
            return f"{block}\n"

        if position == "top":
            if existing_content.startswith("\n"):
                return f"{block}\n{existing_content}"
            else:
                return f"{block}\n\n{existing_content}"
        else:
            # Append at bottom without stripping existing_content
            if existing_content.endswith("\n\n"):
                return f"{existing_content}{block}\n"
            elif existing_content.endswith("\n"):
                return f"{existing_content}\n{block}\n"
            else:
                return f"{existing_content}\n\n{block}\n"


def parse_key_val_args(args_list: Optional[List[str]]) -> Dict[str, str]:
    """Parse KEY=VAL string pairs into a dictionary."""
    result = {}
    if not args_list:
        return result
    for item in args_list:
        if "=" in item:
            k, v = item.split("=", 1)
            result[k.strip()] = v.strip()
        else:
            result[item.strip()] = "true"
    return result


def apply_substitutions(text: str, substitutions: Dict[str, str]) -> str:
    """Replace {KEY} placeholders with their corresponding values."""
    for key, val in substitutions.items():
        text = text.replace(f"{{{key}}}", val)
    # Default fallback for {pm} if unsupplied
    if "{pm}" in text:
        text = text.replace("{pm}", "npm")
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic marker-based content upsert tool")
    parser.add_argument("--file", required=True, help="Target file path")
    parser.add_argument("--content", help="Content string to place inside markers")
    parser.add_argument("--content-file", help="Path to file whose content to place inside markers")
    parser.add_argument("--marker-id", default="stack-guidelines", help="Marker prefix identifier (default: stack-guidelines)")
    parser.add_argument("--position", choices=["top", "bottom"], default="bottom", help="Position if markers not present (default: bottom)")
    parser.add_argument("--header-meta", nargs="*", help="Optional metadata attributes as key=value pairs for start marker")
    parser.add_argument("--substitute", "-s", nargs="*", help="Key=value template substitutions for {key} in content (e.g. pm=pnpm)")
    parser.add_argument("--hash", action="store_true", help="Automatically compute content hash and append to marker metadata")
    parser.add_argument("--dry-run", action="store_true", help="Print diff without writing; exit 0 if up-to-date, 1 if changes needed")
    parser.add_argument("--remove", action="store_true", help="Remove the managed block and markers")

    args = parser.parse_args()
    target_path = Path(args.file)

    inner_content = ""
    if not args.remove:
        if args.content_file:
            cpath = Path(args.content_file)
            if not cpath.exists():
                sys.stderr.write(f"Error: content file '{args.content_file}' not found.\n")
                return 1
            inner_content = cpath.read_text(encoding="utf-8")
        elif args.content is not None:
            inner_content = args.content
        else:
            sys.stderr.write("Error: either --content, --content-file, or --remove must be provided.\n")
            return 1

    substitutions = parse_key_val_args(args.substitute)
    if substitutions or "{pm}" in inner_content:
        inner_content = apply_substitutions(inner_content, substitutions)

    meta = parse_key_val_args(args.header_meta)
    if args.hash and not args.remove:
        meta["hash"] = compute_content_hash(inner_content)

    existing_content = ""
    if target_path.exists():
        existing_content = target_path.read_text(encoding="utf-8")

    updated_content = apply_upsert(
        existing_content=existing_content,
        new_inner_content=inner_content,
        marker_id=args.marker_id,
        position=args.position,
        meta=meta,
        remove=args.remove
    )

    is_identical = (existing_content == updated_content)

    if args.dry_run:
        if is_identical:
            print("Status: Up to date. No changes needed.")
            return 0
        else:
            diff = difflib.unified_diff(
                existing_content.splitlines(keepends=True),
                updated_content.splitlines(keepends=True),
                fromfile=f"a/{args.file}",
                tofile=f"b/{args.file}"
            )
            sys.stdout.writelines(diff)
            return 1

    if is_identical:
        # File is already up to date, do not re-touch file
        return 0

    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(updated_content, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
