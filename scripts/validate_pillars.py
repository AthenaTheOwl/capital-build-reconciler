from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml


def _front_matter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing YAML front matter")

    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError(f"{path}: unterminated YAML front matter")

    data = yaml.load(text[4:end], Loader=yaml.BaseLoader)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: front matter is not a mapping")
    return data


def validate(path: Path) -> list[str]:
    data = _front_matter(path)
    pillars = data.get("pillars")
    if not isinstance(pillars, dict):
        return [f"{path}: missing pillars mapping"]

    errors: list[str] = []
    for key, pillar in pillars.items():
        if not isinstance(pillar, dict):
            errors.append(f"{path}:{key}: pillar entry is not a mapping")
            continue

        verdict = pillar.get("verdict")
        evidence = pillar.get("evidence")
        if not isinstance(evidence, list):
            errors.append(f"{path}:{key}: evidence is not a list")
            continue

        if verdict == "ABSTAIN" and len(evidence) >= 2:
            errors.append(f"{path}:{key}: ABSTAIN has enough evidence for a verdict")
        elif verdict != "ABSTAIN" and len(evidence) < 2:
            errors.append(f"{path}:{key}: {verdict} needs at least two evidence refs")
    return errors


def main(argv: list[str] | None = None) -> int:
    args = [Path(arg) for arg in (argv if argv is not None else sys.argv[1:])]
    if not args:
        print("usage: validate_pillars.py <memo.md> [...]", file=sys.stderr)
        return 2

    errors: list[str] = []
    for path in args:
        try:
            errors.extend(validate(path))
        except Exception as exc:
            errors.append(str(exc))

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
