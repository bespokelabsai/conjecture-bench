#!/usr/bin/env python3
"""Write every problem in the release as one normalized JSONL stream.

The three record kinds have different shapes, so loading them all normally
means three loaders. This script flattens them to one line per problem with
the same nine fields, and prints to stdout:

    python3 scripts/export_records.py > problems.jsonl

Fields: id, kind, title, statement (may be null when the record only points at
its source), url, source, status, status_as_of, record_path. The full detail
always stays in the record file named by record_path.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def emit(row: dict) -> None:
    sys.stdout.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    for path in sorted((ROOT / "problems" / "conjectures").glob("cb-*.json")):
        task = json.loads(path.read_text(encoding="utf-8"))
        status = task.get("status_observation") or {}
        sources = (task.get("provenance") or {}).get("sources") or []
        emit(
            {
                "id": task["id"],
                "kind": "conjecture",
                "title": task.get("title"),
                "statement": task.get("statement"),
                "url": sources[0]["url"] if sources else None,
                "source": (task.get("provenance") or {}).get("collection"),
                "status": status.get("state"),
                "status_as_of": status.get("as_of"),
                "record_path": path.relative_to(ROOT).as_posix(),
            }
        )

    for records in sorted((ROOT / "problems" / "families").glob("*/records.json")):
        payload = json.loads(records.read_text(encoding="utf-8"))
        for record in payload["records"]:
            emit(
                {
                    "id": record["id"],
                    "kind": "family",
                    "title": record.get("title"),
                    "statement": record.get("statement"),
                    "url": (record.get("evidence") or {}).get("url"),
                    "source": payload["source"],
                    "status": (record.get("status") or {}).get("state"),
                    "status_as_of": (record.get("status") or {}).get("as_of"),
                    "record_path": records.relative_to(ROOT).as_posix(),
                }
            )

    catalog = ROOT / "problems" / "extended-catalog"
    for path in sorted(catalog.glob("*/*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        status = record.get("status_observation") or {}
        emit(
            {
                "id": record["id"],
                "kind": "catalog",
                "title": record.get("title"),
                "statement": (record.get("statement") or {}).get("text"),
                "url": (record.get("provenance") or {}).get("context_url")
                or (record.get("provenance") or {}).get("source_url"),
                "source": record.get("source_registry"),
                "status": status.get("state"),
                "status_as_of": status.get("as_of"),
                "record_path": path.relative_to(ROOT).as_posix(),
            }
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
