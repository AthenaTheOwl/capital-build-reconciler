from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .ingest.helicone import ingest
from .show import show

# repo root is two parents up from this file: src/capital_reconcile/cli.py
_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCHEMAS_DIR = _REPO_ROOT / "schemas"


def _ingest(args: argparse.Namespace) -> int:
    try:
        events = ingest(args.raw, args.out)
    except (OSError, ValueError) as exc:
        # OSError: --raw missing or unreadable; ValueError: a log file is
        # malformed JSON or holds a non-object record
        print(f"ingest: {args.raw}: {exc}", file=sys.stderr)
        return 1
    print(f"wrote {len(events)} normalized events to {args.out}")
    return 0


def _show(_args: argparse.Namespace) -> int:
    return show()


def _not_implemented(command: str) -> int:
    raise NotImplementedError(f"{command} is reserved for a later PR")


def _validate_bundled_schemas() -> int:
    """No-arg canonical check: assert the committed JSON schemas are well-formed.

    Read-only, no network, no writes. This is the first user action and only
    touches committed artifacts in ``schemas/``.
    """
    from jsonschema import Draft202012Validator

    schema_files = sorted(_SCHEMAS_DIR.glob("*.schema.json"))
    if not schema_files:
        print(f"validate: no schemas found under {_SCHEMAS_DIR}")
        return 1

    errors: list[str] = []
    for path in schema_files:
        try:
            Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))
        except Exception as exc:  # jsonschema raises several error types
            errors.append(f"{path.name}: invalid JSON Schema: {exc}")

    if errors:
        print("\n".join(errors))
        return 1

    print(f"validate: ok ({len(schema_files)} bundled schemas well-formed)")
    return 0


def _validate_memo(memo: Path) -> int:
    """Validate a memo's YAML front matter against the monthly_memo schema."""
    import yaml
    from jsonschema import Draft202012Validator, FormatChecker

    schema = json.loads((_SCHEMAS_DIR / "monthly_memo.schema.json").read_text(encoding="utf-8"))
    try:
        text = memo.read_text(encoding="utf-8")
    except OSError as exc:
        # missing path, a directory, or an unreadable file
        print(f"validate: {memo}: {exc}")
        return 1
    if not text.startswith("---\n"):
        print(f"validate: {memo}: missing YAML front matter")
        return 1
    end = text.find("\n---", 4)
    if end == -1:
        print(f"validate: {memo}: unterminated YAML front matter")
        return 1
    data = yaml.load(text[4:end], Loader=yaml.BaseLoader)

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = [error.message for error in validator.iter_errors(data)]
    if errors:
        for msg in errors:
            print(f"validate: {memo}: {msg}")
        return 1

    print(f"validate: ok ({memo})")
    return 0


def _validate(args: argparse.Namespace) -> int:
    if args.memo is None:
        return _validate_bundled_schemas()
    return _validate_memo(args.memo)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="capital_reconcile")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="normalize Helicone-style JSON logs")
    ingest_parser.add_argument("--provider", choices=["anthropic"], required=True)
    ingest_parser.add_argument("--raw", type=Path, required=True)
    ingest_parser.add_argument("--out", type=Path, required=True)
    ingest_parser.set_defaults(func=_ingest)

    show_parser = subparsers.add_parser(
        "show",
        help="print a readable, ranked per-region view of the committed telemetry",
    )
    show_parser.set_defaults(func=_show)

    score_parser = subparsers.add_parser("score", help="reserved scorer surface")
    score_parser.add_argument("--month", required=True)
    score_parser.add_argument("--pillars", type=Path, required=True)
    score_parser.add_argument("--normalized", type=Path, required=True)
    score_parser.add_argument("--out", type=Path, required=True)
    score_parser.set_defaults(func=lambda _args: _not_implemented("score"))

    validate_parser = subparsers.add_parser(
        "validate",
        help="validate committed artifacts; with no memo, check the bundled schemas",
    )
    validate_parser.add_argument(
        "memo",
        type=Path,
        nargs="?",
        default=None,
        help="optional memo to validate; defaults to the bundled schemas when omitted",
    )
    validate_parser.set_defaults(func=_validate)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
