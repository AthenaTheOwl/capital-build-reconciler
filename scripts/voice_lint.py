from __future__ import annotations

import re
import sys
from pathlib import Path


BANNED_TERMS = [
    "best-in-class",
    "cutting-edge",
    "game-changing",
    "leverage",
    "revolutionary",
    "seamless",
    "synergy",
    "unlock",
    "world-class",
]

ANTITHETICAL_REVERSAL = re.compile(r"\bnot\s+(?:only|just|merely)\b.{0,100}\bbut\b", re.IGNORECASE)
BANNED_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(term) for term in BANNED_TERMS) + r")\b",
    re.IGNORECASE,
)


def _iter_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(
                item
                for item in path.rglob("*")
                if item.is_file() and item.suffix.lower() in {".md", ".py", ".yaml", ".yml"}
            )
        else:
            files.append(path)
    return files


def lint_file(path: Path) -> list[str]:
    errors: list[str] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        for match in BANNED_PATTERN.finditer(line):
            errors.append(f"{path}:{line_no}: banned term: {match.group(1)}")
        if ANTITHETICAL_REVERSAL.search(line):
            errors.append(f"{path}:{line_no}: antithetical reversal")
    return errors


def main(argv: list[str] | None = None) -> int:
    args = [Path(arg) for arg in (argv if argv is not None else sys.argv[1:])]
    if not args:
        print("usage: voice_lint.py <file-or-directory> [...]", file=sys.stderr)
        return 2

    errors: list[str] = []
    for path in _iter_files(args):
        errors.extend(lint_file(path))

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
