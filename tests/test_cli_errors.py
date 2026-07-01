from __future__ import annotations

from pathlib import Path

from capital_reconcile.cli import main


def test_ingest_malformed_json_returns_one(tmp_path: Path, capsys) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "bad.json").write_text("{ not valid json", encoding="utf-8")
    out = tmp_path / "out.parquet"

    rc = main(["ingest", "--provider", "anthropic", "--raw", str(raw), "--out", str(out)])

    assert rc == 1
    err = capsys.readouterr().err
    assert "bad.json" in err
    assert "not valid JSON" in err
    assert not out.exists()


def test_validate_missing_memo_returns_one(tmp_path: Path, capsys) -> None:
    missing = tmp_path / "nope.md"

    rc = main(["validate", str(missing)])

    assert rc == 1
    assert str(missing) in capsys.readouterr().out
