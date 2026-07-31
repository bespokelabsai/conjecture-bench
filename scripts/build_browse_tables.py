#!/usr/bin/env python3
"""Generate the browsable tables covering every problem in the repository.

They exist so the collection can be sorted and filtered without running
anything.  They are generated, never authored: every cell is copied from a
record, or is one subtraction of two published bounds.  Nothing here is
inferred, estimated, or judged.

Three kinds of record are covered, and they are not interchangeable:

- ``conjecture``: an individually curated conjecture.
- ``family``: one instance of a sourced mathematical family.
- ``catalog``: a sourced entry in ``problems/extended-catalog/``.

Two tiers, because one flat table cannot hold ``gap`` safely:

- ``all.csv`` covers every record, with only the columns that mean the same
  thing for all three kinds.  It carries no gap.
- ``<family>.csv`` adds the gap for one database family, with the unit written
  into the column name.  Within one file every row shares a unit, so sorting by
  gap is exactly right.

Why the split matters: a gap of 2 in linear codes and 179 in constant weight
codes are not comparable, because one counts Hamming distance and the other
counts codewords.  A single sortable column inviting that comparison would be a
trap, and GitHub's CSV viewer sorts one column at a time.

``gap`` always means the same thing: the width of the interval that the true
value is known to lie in.  A gap of 1 is one step from settled.  It is not a
difficulty score; a wide gap can also mean nobody has a good bound argument
yet.

Only database families have bounds, so no gap appears anywhere else, and
existence families carry no gap column at all rather than a column of blanks.

Usage::

    python3 scripts/build_browse_tables.py            # write the index
    python3 scripts/build_browse_tables.py --check    # fail if it is stale
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "problems" / "families"
TASK_ROOT = ROOT / "problems" / "conjectures"
DISCOVERY_ROOT = ROOT / "problems" / "extended-catalog"
INDEX_ROOT = ROOT / "problems" / "tables"

GENERAL_COLUMNS = ["id", "kind", "title", "source", "family", "status"]

# Per family: which two target keys bracket the interval the true value lies in,
# and the unit that interval is measured in.  The unit becomes part of the
# column name so it cannot be read off the wrong axis.
#
#   (lower key, upper key, unit)
#
# Coverings publish a floor and a record above it, so the record is the upper
# end. Codes publish a record and a ceiling above it, so the record is the
# lower end. Either way the gap is the width of the unknown window.
GAP_SPEC: dict[str, tuple[str, str, str]] = {
    "covering-design": ("lower_bound", "best_known", "blocks"),
    "linear-code": ("best_known", "upper_bound", "distance"),
    "linear-code-nonbinary": ("best_known", "upper_bound", "distance"),
    "constant-weight-code": ("best_known", "upper_bound", "codewords"),
    "ramsey-number": ("best_known", "upper_bound", "vertices"),
}


def load_records() -> list[dict[str, Any]]:
    rows = []
    for path in sorted(SOURCE_ROOT.glob("*/records.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        for record in payload["records"]:
            rows.append((payload["source"], record))
    return rows


def general_row(source: str, record: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": record["id"],
        "kind": "family",
        "title": record.get("title", ""),
        "source": source,
        "family": record["class"],
        "status": (record.get("status") or {}).get("state", ""),
    }


def task_rows() -> list[dict[str, Any]]:
    """Individually curated conjectures, one file each."""
    rows = []
    for path in sorted(TASK_ROOT.glob("cb-*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        rows.append(
            {
                "id": record["id"],
                "kind": "conjecture",
                "title": record.get("title", ""),
                "source": (record.get("provenance") or {}).get("collection", ""),
                "family": "",
                "status": (record.get("status_observation") or {}).get("state", ""),
            }
        )
    return rows


def discovery_rows() -> list[dict[str, Any]]:
    """Sourced pointers to problems."""
    rows = []
    for path in sorted(DISCOVERY_ROOT.glob("*/*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        rows.append(
            {
                "id": record["id"],
                "kind": "catalog",
                "title": record.get("title", ""),
                "source": record["source_registry"],
                "family": "",
                "status": (record.get("status_observation") or {}).get("state", ""),
            }
        )
    return rows


def family_row(source: str, record: dict[str, Any], spec: tuple[str, str, str] | None) -> dict[str, Any]:
    row = {
        "id": record["id"],
        "source": source,
    }
    if spec is None:
        return row

    lower_key, upper_key, unit = spec
    target = record.get("frontier") or {}
    lower, upper = target.get(lower_key), target.get(upper_key)
    if isinstance(lower, int) and isinstance(upper, int):
        row["best_known"] = target["best_known"]
        row[f"gap_{unit}"] = upper - lower
    else:
        # Reference-only rows in a family that otherwise has bounds, such as the
        # Ramsey pairs too large to search.  Left empty rather than guessed.
        row["best_known"] = ""
        row[f"gap_{unit}"] = ""
    return row


def render(columns: list[str], rows: list[dict[str, Any]]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def build() -> dict[str, str]:
    """Return the full index as a mapping of filename to file content."""
    records = load_records()
    files: dict[str, str] = {}

    general = [general_row(source, record) for source, record in records]
    general += task_rows()
    general += discovery_rows()
    general.sort(key=lambda row: (row["kind"], row["id"]))
    files["all.csv"] = render(GENERAL_COLUMNS, general)

    # A file per kind for the kinds that have no other breakdown.  Family rows
    # are not duplicated here, because the per-family files below carry more.
    # all.csv holds everything but is too large for GitHub to render, so the
    # smaller files are what people actually browse.
    rows = [row for row in general if row["kind"] == "conjecture"]
    files["kind-conjecture.csv"] = render(GENERAL_COLUMNS, rows)

    # The catalog is split per source to stay under GitHub's rendering limit.
    catalog = [row for row in general if row["kind"] == "catalog"]
    by_source: dict[str, list[dict[str, Any]]] = {}
    for row in catalog:
        by_source.setdefault(row["source"], []).append(row)
    for source, rows in sorted(by_source.items()):
        rows.sort(key=lambda row: row["id"])
        files[f"catalog-{source}.csv"] = render(GENERAL_COLUMNS, rows)

    by_family: dict[str, list[dict[str, Any]]] = {}
    for source, record in records:
        by_family.setdefault(record["class"], []).append((source, record))

    for family, entries in sorted(by_family.items()):
        spec = GAP_SPEC.get(family)
        columns = ["id", "source"]
        if spec is not None:
            columns += ["best_known", f"gap_{spec[2]}"]
        rows = [family_row(source, record, spec) for source, record in entries]
        if spec is not None:
            # GitHub's CSV viewer has a search box but no column sorting, so
            # the file itself is sorted by gap, smallest first. The problems
            # closest to being settled are then the first thing a reader sees.
            gap_key = f"gap_{spec[2]}"
            rows.sort(key=lambda row: (row[gap_key] == "", row[gap_key] if row[gap_key] == "" else int(row[gap_key]), row["id"]))
        else:
            rows.sort(key=lambda row: row["id"])
        files[f"{family}.csv"] = render(columns, rows)

    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the committed index is stale")
    arguments = parser.parse_args()

    files = build()
    if arguments.check:
        stale = []
        for name, content in sorted(files.items()):
            path = INDEX_ROOT / name
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                stale.append(name)
        existing = {path.name for path in INDEX_ROOT.glob("*.csv")} if INDEX_ROOT.is_dir() else set()
        for name in sorted(existing - set(files)):
            stale.append(f"{name} (no longer generated)")
        if stale:
            print(f"index is stale: {', '.join(stale)}; run scripts/build_browse_tables.py", file=sys.stderr)
            return 1
        rows = files["all.csv"].count("\n") - 1
        print(f"browse tables ok: {len(files)} files, {rows} records")
        return 0

    INDEX_ROOT.mkdir(parents=True, exist_ok=True)
    for name, content in sorted(files.items()):
        (INDEX_ROOT / name).write_text(content, encoding="utf-8")
        print(f"wrote {(INDEX_ROOT / name).relative_to(ROOT)}")
    for path in sorted(INDEX_ROOT.glob("*.csv")):
        if path.name not in files:
            path.unlink()
            print(f"removed {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
