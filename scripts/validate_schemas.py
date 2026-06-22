from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
MONTHLY_MEMO_SCHEMA = ROOT / "schemas" / "monthly_memo.schema.json"


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


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: schema root is not a JSON object")
    return data


def validate_schema_file(path: Path) -> list[str]:
    try:
        Draft202012Validator.check_schema(_load_json(path))
    except Exception as exc:  # jsonschema raises several validation error types.
        return [f"{path}: invalid JSON Schema: {exc}"]
    return []


def validate_memo(path: Path) -> list[str]:
    try:
        schema = _load_json(MONTHLY_MEMO_SCHEMA)
        data = _front_matter(path)
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        return [f"{path}: {error.message}" for error in validator.iter_errors(data)]
    except Exception as exc:
        return [str(exc)]


def _targets(path: Path) -> list[Path]:
    if path.is_dir():
        return sorted(path.glob("*.schema.json"))
    return [path]


def main(argv: list[str] | None = None) -> int:
    args = [Path(arg) for arg in (argv if argv is not None else sys.argv[1:])]
    if not args:
        print("usage: validate_schemas.py <schema-dir-or-memo> [...]", file=sys.stderr)
        return 2

    errors: list[str] = []
    for arg in args:
        for path in _targets(arg):
            if path.suffix == ".md":
                errors.extend(validate_memo(path))
            else:
                errors.extend(validate_schema_file(path))

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
