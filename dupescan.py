#!/usr/bin/env python3
"""Find identical files in a directory without modifying them."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


CHUNK_SIZE = 1024 * 1024


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scan_directory(root: Path, min_size: int = 1) -> dict[str, Any]:
    """Return duplicate groups and scan errors for files at least min_size bytes."""
    by_size: dict[int, list[Path]] = defaultdict(list)
    errors: list[dict[str, str]] = []
    scanned_files = 0
    total_bytes = 0

    def record_walk_error(error: OSError) -> None:
        errors.append({"path": str(error.filename or root), "error": str(error)})

    for current, directories, filenames in os.walk(
        root, followlinks=False, onerror=record_walk_error
    ):
        current_path = Path(current)
        directories[:] = [
            name for name in directories if not (current_path / name).is_symlink()
        ]
        for filename in filenames:
            path = current_path / filename
            try:
                if path.is_symlink() or not path.is_file():
                    continue
                size = path.stat().st_size
                if size < min_size:
                    continue
            except OSError as error:
                errors.append({"path": str(path), "error": str(error)})
                continue
            scanned_files += 1
            total_bytes += size
            by_size[size].append(path)

    duplicate_groups: list[dict[str, Any]] = []
    for size, paths in sorted(by_size.items()):
        if len(paths) < 2:
            continue
        by_hash: dict[str, list[str]] = defaultdict(list)
        for path in sorted(paths, key=lambda item: str(item).casefold()):
            try:
                by_hash[_sha256(path)].append(str(path))
            except OSError as error:
                errors.append({"path": str(path), "error": str(error)})
        for digest, matches in sorted(by_hash.items()):
            if len(matches) > 1:
                duplicate_groups.append(
                    {"size_bytes": size, "sha256": digest, "paths": matches}
                )

    duplicate_groups.sort(
        key=lambda group: (group["size_bytes"], group["paths"][0].casefold())
    )
    duplicate_bytes = sum(
        group["size_bytes"] * (len(group["paths"]) - 1)
        for group in duplicate_groups
    )
    return {
        "root": str(root),
        "scanned_files": scanned_files,
        "total_bytes": total_bytes,
        "duplicate_groups": duplicate_groups,
        "duplicate_bytes": duplicate_bytes,
        "errors": errors,
    }


def _format_bytes(size: int) -> str:
    units = ("B", "KB", "MB", "GB", "TB")
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{size} B"
        value /= 1024
    return f"{size} B"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Find identical files without changing or deleting them."
    )
    parser.add_argument("directory", type=Path, help="directory to scan recursively")
    parser.add_argument(
        "--min-size",
        type=int,
        default=1,
        metavar="BYTES",
        help="ignore files smaller than this size (default: 1 byte)",
    )
    parser.add_argument(
        "--json", action="store_true", help="print the report as JSON"
    )
    args = parser.parse_args(argv)
    if args.min_size < 0:
        parser.error("--min-size must be zero or greater")
    if not args.directory.is_dir():
        parser.error(f"not a directory: {args.directory}")

    report = scan_directory(args.directory, args.min_size)
    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    print(f"Scanned {report['scanned_files']} files in {report['root']}")
    if report["duplicate_groups"]:
        print(
            f"Found {len(report['duplicate_groups'])} duplicate group(s); "
            f"potential savings: {_format_bytes(report['duplicate_bytes'])}"
        )
        for group in report["duplicate_groups"]:
            print(f"\n{_format_bytes(group['size_bytes'])} each")
            for path in group["paths"]:
                print(f"  {path}")
    else:
        print("No duplicate files found.")

    if report["errors"]:
        print(f"\nCould not read {len(report['errors'])} path(s):", file=sys.stderr)
        for error in report["errors"]:
            print(f"  {error['path']}: {error['error']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
