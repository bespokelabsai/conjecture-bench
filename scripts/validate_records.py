#!/usr/bin/env python3
"""Validate every committed ConjectureBench record offline."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "problems" / "schemas"
CONJECTURES = ROOT / "problems" / "conjectures"
FAMILIES = ROOT / "problems" / "families"
CATALOG = ROOT / "problems" / "extended-catalog"

CATALOG_SOURCES = {
    "egres-open": "egres-open",
    "erdos-problems": "erdos-problems",
    "formal-conjectures": "formal-conjectures-bench-v1",
    "kourovka-notebook": "kourovka-notebook-21",
    "open-problems-project": "open-problems-project",
    "unsolvedmath": "unsolvedmath-1.1.0",
}
ALLOWED_CATALOG_STATES = {
    "conflicting-status-categories",
    "listed-open",
    "listed-unsolved",
    "open",
    "partially-open",
    "research open",
    "reported-answered-by-source",
    "unclear",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validator(name: str) -> jsonschema.Draft202012Validator:
    schema = load(SCHEMAS / name)
    jsonschema.Draft202012Validator.check_schema(schema)
    return jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    )


def schema_errors(
    check: jsonschema.Draft202012Validator,
    value: Any,
    label: str,
) -> list[str]:
    return [
        f"{label}{error.json_path[1:]}: {error.message}"
        for error in sorted(check.iter_errors(value), key=lambda item: list(item.path))
    ]


def main() -> int:
    errors: list[str] = []
    identifiers: dict[str, str] = {}
    conjectures: dict[str, dict[str, Any]] = {}
    related: list[tuple[str, str]] = []
    catalog_count = 0
    family_count = 0

    checks = {
        "conjecture": validator("conjecture.schema.json"),
        "catalog": validator("catalog.schema.json"),
        "family": validator("family.schema.json"),
        "source": validator("source.schema.json"),
    }

    def register(identifier: str, label: str) -> None:
        if identifier in identifiers:
            errors.append(
                f"{label}: duplicate ID; first used by {identifiers[identifier]}"
            )
        else:
            identifiers[identifier] = label

    for path in sorted(CONJECTURES.glob("cb-*.json")):
        label = path.relative_to(ROOT).as_posix()
        try:
            record = load(path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{label}: {exc}")
            continue
        errors.extend(schema_errors(checks["conjecture"], record, label))
        identifier = record.get("id")
        if isinstance(identifier, str):
            register(identifier, label)
            conjectures[identifier] = record
            if path.stem != identifier:
                errors.append(f"{label}: filename does not match ID")

    for identifier, record in sorted(conjectures.items()):
        duplicate = record.get("duplicate_of")
        if duplicate is None:
            continue
        target = conjectures.get(duplicate)
        if target is None:
            errors.append(f"{identifier}: duplicate_of references missing {duplicate}")
        elif record.get("equivalence_group") != target.get("equivalence_group"):
            errors.append(f"{identifier}: duplicate pair needs one equivalence_group")

    for directory_name, source_name in CATALOG_SOURCES.items():
        directory = CATALOG / directory_name
        for path in sorted(directory.glob("*.json")):
            catalog_count += 1
            label = path.relative_to(ROOT).as_posix()
            try:
                record = load(path)
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"{label}: {exc}")
                continue
            errors.extend(schema_errors(checks["catalog"], record, label))
            identifier = record.get("id")
            if isinstance(identifier, str):
                register(identifier, label)
                if path.stem != identifier:
                    errors.append(f"{label}: filename does not match ID")
            if record.get("source_registry") != source_name:
                errors.append(f"{label}: source_registry does not match directory")
            if (
                record.get("status_observation", {}).get("state")
                not in ALLOWED_CATALOG_STATES
            ):
                errors.append(f"{label}: unsupported catalog status")
            for target in record.get("related_conjecture_ids", []):
                related.append((label, target))

    for directory in sorted(path for path in FAMILIES.iterdir() if path.is_dir()):
        records_path = directory / "records.json"
        source_path = directory / "source.json"
        label = records_path.relative_to(ROOT).as_posix()
        try:
            payload = load(records_path)
            source = load(source_path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{directory.relative_to(ROOT)}: {exc}")
            continue
        errors.extend(schema_errors(checks["family"], payload, label))
        errors.extend(
            schema_errors(
                checks["source"], source, source_path.relative_to(ROOT).as_posix()
            )
        )
        if payload.get("source") != directory.name or source.get("slug") != directory.name:
            errors.append(f"{label}: source slug does not match directory")
        for record in payload.get("records", []):
            family_count += 1
            identifier = record.get("id")
            if isinstance(identifier, str):
                register(identifier, label)

    for label, target in related:
        if target not in conjectures:
            errors.append(f"{label}: related conjecture {target} does not exist")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(
        f"records ok: {len(identifiers)} total "
        f"({len(conjectures)} conjectures, "
        f"{family_count} family records, {catalog_count} catalog records)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
