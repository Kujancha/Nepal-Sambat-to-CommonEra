"""Regression tests for documented concordances used to develop v0.4.
These are calibration checks, not an independent historical validation sample.
"""
import csv
from pathlib import Path
import pytest
from nschron import convert

DATA = Path(__file__).resolve().parents[1] / "data" / "historical_concordances.csv"

with DATA.open(encoding="utf-8", newline="") as stream:
    RECORDS = list(csv.DictReader(stream))

@pytest.mark.parametrize("row", [r for r in RECORDS if r["classification"] in ("exact", "qualified_exact", "ns_weekday_match")], ids=lambda row: row["id"])
def test_recorded_matches(row):
    candidates = convert(int(row["ns_year"]), row["paksha"], int(row["tithi"]), row["month"])
    assert row["reported_ce_date"] in {c.gregorian for c in candidates}
    if row["id"] == "jaya_prakash_1750":
        assert next(c for c in candidates if c.gregorian == "1750-05-01").weekday == "Friday"

def test_unresolved_bhaktapur_stays_unresolved():
    assert convert(858, "shukla", 7, "Kartika") == []
