from __future__ import annotations

import argparse

from capital_reconcile.cli import build_parser as _build_reconcile_parser


def build_parser() -> argparse.ArgumentParser:
    parser = _build_reconcile_parser()
    parser.prog = "capital-build-reconciler"
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
