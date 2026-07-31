# Schemas

The JSON contracts for every record type in the release. Each record kind maps
to one schema:

| Record kind | Lives in | Schema |
| --- | --- | --- |
| conjecture | `problems/conjectures/cb-NNNN.json` | `conjecture.schema.json` |
| family | `problems/families/<name>/records.json` | `family.schema.json` and `source.schema.json` |
| catalog | `problems/extended-catalog/<source>/*.json` | `catalog.schema.json` |

To load all 14,865 records as one flat stream, one line per record:

```bash
python3 scripts/export_records.py > problems.jsonl
```
