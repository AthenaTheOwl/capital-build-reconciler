from __future__ import annotations

import argparse
from pathlib import Path

from .ingest.helicone import ingest


def _ingest(args: argparse.Namespace) -> int:
    events = ingest(args.raw, args.out)
    print(f"wrote {len(events)} normalized events to {args.out}")
    return 0


def _not_implemented(command: str) -> int:
    raise NotImplementedError(f"{command} is reserved for a later PR")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="capital_reconcile")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="normalize Helicone-style JSON logs")
    ingest_parser.add_argument("--provider", choices=["anthropic"], required=True)
    ingest_parser.add_argument("--raw", type=Path, required=True)
    ingest_parser.add_argument("--out", type=Path, required=True)
    ingest_parser.set_defaults(func=_ingest)

    score_parser = subparsers.add_parser("score", help="reserved scorer surface")
    score_parser.add_argument("--month", required=True)
    score_parser.add_argument("--pillars", type=Path, required=True)
    score_parser.add_argument("--normalized", type=Path, required=True)
    score_parser.add_argument("--out", type=Path, required=True)
    score_parser.set_defaults(func=lambda _args: _not_implemented("score"))

    validate_parser = subparsers.add_parser("validate", help="reserved memo validator surface")
    validate_parser.add_argument("memo", type=Path)
    validate_parser.set_defaults(func=lambda _args: _not_implemented("validate"))

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
