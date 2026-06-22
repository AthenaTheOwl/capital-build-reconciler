from __future__ import annotations

import json
from pathlib import Path

import pyarrow.parquet as pq
from jsonschema import Draft202012Validator, FormatChecker

from capital_reconcile.ingest.helicone import ingest


ROOT = Path(__file__).resolve().parents[1]


def test_ingest_helicone_fixture_writes_schema_valid_parquet(tmp_path: Path) -> None:
    out_path = tmp_path / "out.parquet"

    events = ingest(ROOT / "tests" / "fixtures", out_path)

    assert len(events) == 3
    assert out_path.exists()

    rows = pq.read_table(out_path).to_pylist()
    schema = json.loads((ROOT / "schemas" / "normalized_event.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    assert len(rows) == 3
    assert set(rows[0]) == set(schema["required"])
    assert {row["region"] for row in rows} == {"us-east-1", "us-west-2"}
    assert sum(row["rate_limit_hit"] for row in rows) == 1
    for row in rows:
        validator.validate(row)
