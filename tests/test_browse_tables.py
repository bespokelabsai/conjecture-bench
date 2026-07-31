"""Tests for the generated index.

The index is only worth having if every cell traces back to a record, so these
tests re-derive the interesting column independently rather than trusting the
generator: they recompute each gap straight from ``records.json`` and compare.

They also pin the two properties that make the two-tier split work, since both
are easy to break by accident:

- the general table carries no gap column, so nothing invites a comparison
  across families; and
- a family whose problems are existence questions carries no gap column at all,
  rather than a column of blanks.
"""

from __future__ import annotations

import collections
import csv
import io
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_browse_tables import (  # noqa: E402
    GAP_SPEC,
    GENERAL_COLUMNS,
    build,
    discovery_rows,
    task_rows,
)

SOURCE_ROOT = ROOT / "problems" / "families"
INDEX_ROOT = ROOT / "problems" / "tables"

# Files that list records by kind rather than by family, so they carry no gap.
KIND_FILES = {"kind-conjecture.csv"} | {f"catalog-{s}.csv" for s in ("egres-open","erdos-problems","formal-conjectures-bench-v1","kourovka-notebook-21","open-problems-project","unsolvedmath-1.1.0")}

# Families whose task is to exhibit an object, so there are no bounds to narrow.
EXISTENCE_FAMILIES = {"abelian-difference-set"}


def read(content: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(content)))


class IndexTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.files = build()
        cls.records = {}
        for path in sorted(SOURCE_ROOT.glob("*/records.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            for record in payload["records"]:
                cls.records[record["id"]] = (payload["source"], record)

    def test_committed_index_is_current(self):
        for name, content in self.files.items():
            with self.subTest(name):
                path = INDEX_ROOT / name
                self.assertTrue(path.is_file(), f"{name} has not been generated")
                self.assertEqual(path.read_text(encoding="utf-8"), content, f"{name} is stale")

    def test_no_stale_files_left_behind(self):
        present = {path.name for path in INDEX_ROOT.glob("*.csv")}
        self.assertEqual(present, set(self.files))

    def test_general_table_covers_all_three_kinds(self):
        rows = read(self.files["all.csv"])
        self.assertEqual(list(rows[0]), GENERAL_COLUMNS)
        by_kind = collections.Counter(row["kind"] for row in rows)
        self.assertEqual(by_kind["family"], len(self.records))
        self.assertEqual(by_kind["conjecture"], len(task_rows()))
        self.assertEqual(by_kind["catalog"], len(discovery_rows()))
        self.assertEqual(len(rows), sum(by_kind.values()))
        # Ids are unique across the whole collection, not just within a kind.
        self.assertEqual(len({row["id"] for row in rows}), len(rows))

    def test_every_database_record_appears(self):
        rows = read(self.files["all.csv"])
        present = {row["id"] for row in rows if row["kind"] == "family"}
        self.assertEqual(present, set(self.records))

    def test_kind_files_match_the_general_table(self):
        rows = read(self.files["all.csv"])
        for name in KIND_FILES:
            with self.subTest(name):
                got = read(self.files[name])
                if name.startswith("kind-"):
                    kind = name[len("kind-") : -len(".csv")]
                    expected = [row for row in rows if row["kind"] == kind]
                    self.assertEqual(got, expected)
                else:
                    source = name[len("catalog-") : -len(".csv")]
                    expected = {row["id"] for row in rows if row["kind"] == "catalog" and row["source"] == source}
                    self.assertEqual({row["id"] for row in got}, expected)

    def test_general_table_carries_no_gap(self):
        # The whole reason for the two tiers: a gap here would be sortable
        # across families whose units differ, which is meaningless.
        self.assertFalse([column for column in GENERAL_COLUMNS if column.startswith("gap")])

    def test_every_gap_recomputes_from_the_record(self):
        checked = 0
        for name, content in self.files.items():
            if name == "all.csv" or name in KIND_FILES:
                continue
            family = name[: -len(".csv")]
            spec = GAP_SPEC.get(family)
            if spec is None:
                continue
            lower_key, upper_key, unit = spec
            for row in read(content):
                _, record = self.records[row["id"]]
                target = record.get("frontier") or {}
                lower, upper = target.get(lower_key), target.get(upper_key)
                if not (isinstance(lower, int) and isinstance(upper, int)):
                    # Reference-only row: must be blank, never guessed.
                    self.assertEqual(row[f"gap_{unit}"], "")
                    self.assertEqual(row["best_known"], "")
                    continue
                self.assertEqual(int(row[f"gap_{unit}"]), upper - lower, row["id"])
                self.assertEqual(int(row["best_known"]), target["best_known"], row["id"])
                self.assertGreater(upper - lower, 0, f"{row['id']} is not open")
                checked += 1
        self.assertGreater(checked, 6000, "expected thousands of gaps to verify")

    def test_gap_column_names_carry_their_unit(self):
        for name, content in self.files.items():
            if name == "all.csv" or name in KIND_FILES:
                continue
            family = name[: -len(".csv")]
            columns = list(read(content)[0])
            gaps = [column for column in columns if column.startswith("gap_")]
            if family in EXISTENCE_FAMILIES:
                self.assertEqual(gaps, [], f"{family} has no bounds, so it must carry no gap column")
                continue
            self.assertEqual(gaps, [f"gap_{GAP_SPEC[family][2]}"], family)

    def test_generation_is_deterministic(self):
        self.assertEqual(build(), self.files)


if __name__ == "__main__":
    unittest.main()
