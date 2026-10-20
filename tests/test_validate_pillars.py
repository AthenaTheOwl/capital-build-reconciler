from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location(
    "validate_pillars", ROOT / "scripts" / "validate_pillars.py"
)
validate_pillars = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(validate_pillars)

TELEMETRY = "data/normalized/2026-06.parquet#rate_limit_hits_us_east_1"
REPORT = "reports/2026-M06-ingest-summary.jsonl#rate_limit_hits"
PRIOR_MEMO = "capital_reconcile/2026-M05.md#foundry"
EARNINGS = "https://example.com/earnings/2026-Q2-transcript#n3-utilization"


def _memo(tmp_path: Path, verdict: str, evidence: list[str]) -> Path:
    refs = "\n".join(f"      - {ref}" for ref in evidence) if evidence else ""
    block = "    evidence:\n" + refs if evidence else "    evidence: []"
    text = (
        "---\n"
        "month: 2026-06\n"
        "pillars:\n"
        "  foundry:\n"
        f"    verdict: {verdict}\n"
        f"{block}\n"
        '    revert_threshold: "n/a"\n'
        "---\n"
    )
    path = tmp_path / "memo.md"
    path.write_text(text, encoding="utf-8")
    return path


@pytest.mark.parametrize("verdict", ["HOLD", "UPWEIGHT", "TRIM"])
def test_verdict_from_telemetry_alone_is_rejected(tmp_path: Path, verdict: str) -> None:
    errors = validate_pillars.validate(_memo(tmp_path, verdict, [TELEMETRY, REPORT]))
    assert len(errors) == 1
    assert "independent evidence" in errors[0]


def test_telemetry_plus_prior_memo_is_not_independent(tmp_path: Path) -> None:
    errors = validate_pillars.validate(_memo(tmp_path, "UPWEIGHT", [TELEMETRY, PRIOR_MEMO]))
    assert errors and "independent evidence" in errors[0]


def test_verdict_with_independent_evidence_passes(tmp_path: Path) -> None:
    assert validate_pillars.validate(_memo(tmp_path, "HOLD", [TELEMETRY, EARNINGS])) == []


def test_under_evidenced_verdict_is_rejected(tmp_path: Path) -> None:
    errors = validate_pillars.validate(_memo(tmp_path, "HOLD", [EARNINGS]))
    assert errors and "at least two evidence refs" in errors[0]


def test_abstain_may_carry_telemetry_flags(tmp_path: Path) -> None:
    assert validate_pillars.validate(_memo(tmp_path, "ABSTAIN", [TELEMETRY, REPORT])) == []
    assert validate_pillars.validate(_memo(tmp_path, "ABSTAIN", [])) == []


def test_abstain_with_enough_independent_evidence_is_rejected(tmp_path: Path) -> None:
    errors = validate_pillars.validate(_memo(tmp_path, "ABSTAIN", [TELEMETRY, EARNINGS]))
    assert errors and "enough evidence for a verdict" in errors[0]


@pytest.mark.parametrize(
    "ref,telemetry,independent",
    [
        (TELEMETRY, True, False),
        (REPORT, True, False),
        ("./data/raw/anthropic/2026-06/log.json", True, False),
        ("exports/june.parquet", True, False),
        (PRIOR_MEMO, False, False),
        (EARNINGS, False, True),
        ("earnings-pillar-diff/2026-Q2/tsmc.md#n3", False, True),
    ],
)
def test_ref_classification(ref: str, telemetry: bool, independent: bool) -> None:
    assert validate_pillars.is_telemetry_ref(ref) is telemetry
    assert validate_pillars.is_independent_ref(ref) is independent


def test_design_schema_sketch_passes_pillar_validator(tmp_path: Path) -> None:
    # the spec's example front matter must obey the same evidence policy the
    # validator enforces; a sketch that pins a pillar on telemetry fails here
    design = (ROOT / "specs" / "0001-foundation" / "design.md").read_text(encoding="utf-8")
    sketch = re.search(r"^```yaml\n(.*?)^```", design, flags=re.S | re.M)
    assert sketch is not None
    memo = tmp_path / "sketch.md"
    memo.write_text("---\n" + sketch.group(1) + "---\n", encoding="utf-8")
    assert validate_pillars.validate(memo) == []
