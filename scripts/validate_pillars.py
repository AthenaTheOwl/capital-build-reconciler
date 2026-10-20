from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml


# Evidence refs that point at this repo's own telemetry (raw or normalized
# logs, report artifacts). Telemetry can raise a flag or a ranked interval for
# a pillar; it cannot by itself support a pillar verdict (R-CBR-003, R-CBR-011).
TELEMETRY_PREFIXES: tuple[str, ...] = ("data/raw/", "data/normalized/", "reports/")
TELEMETRY_SUFFIXES: tuple[str, ...] = (".parquet", ".jsonl")
# Prior monthly memos restate earlier calls; they are not independent evidence.
MEMO_PREFIX = "capital_reconcile/"


def _ref_path(ref: str) -> str:
    path = ref.split("#", 1)[0].strip()
    while path.startswith("./"):
        path = path[2:]
    return path


def is_telemetry_ref(ref: str) -> bool:
    path = _ref_path(ref)
    return path.startswith(TELEMETRY_PREFIXES) or path.endswith(TELEMETRY_SUFFIXES)


def is_independent_ref(ref: str) -> bool:
    """True for evidence sourced outside this repo's telemetry and memos."""
    path = _ref_path(ref)
    return bool(path) and not is_telemetry_ref(ref) and not path.startswith(MEMO_PREFIX)


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

        independent = [ref for ref in evidence if is_independent_ref(str(ref))]
        if verdict == "ABSTAIN":
            # telemetry flags may ride along with an ABSTAIN; only a pillar
            # with enough evidence including an independent source must call it
            if len(evidence) >= 2 and independent:
                errors.append(f"{path}:{key}: ABSTAIN has enough evidence for a verdict")
        elif len(evidence) < 2:
            errors.append(f"{path}:{key}: {verdict} needs at least two evidence refs")
        elif not independent:
            errors.append(
                f"{path}:{key}: {verdict} cites telemetry or prior memos only; "
                "a pillar verdict needs independent evidence, otherwise ABSTAIN"
            )
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
