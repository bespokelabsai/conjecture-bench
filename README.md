# ConjectureBench

A curated collection of nearly 15,000 open mathematics problems, built to make
them easy to explore. Every record carries a statement or pointer, its source,
and a dated status observation or pinned source revision.

Inclusion does not mean that Bespoke Labs has independently verified a
problem's status or any claimed solution.

## What is in it

14,865 records of three kinds.

| Kind | Count | What it is |
| --- | ---: | --- |
| [Conjectures](problems/conjectures) | 302 | individually curated conjectures, one JSON file each |
| [Families](problems/families) | 9,342 | bound and existence problems from six sourced families |
| [Extended catalog](problems/extended-catalog) | 5,221 | problem statements or pointers from published collections |

All problems come from collections that other people compiled. Records carry
source links, family and catalog sources are credited, and every family record
stores a quote from the page it cites so its claim can be re-checked.

The 652 Erdős catalog records carry pointers instead of statement text.

## Explore

Open a spreadsheet in [`problems/tables/`](problems/tables). GitHub shows each
as a searchable table. Family files with bounds are sorted by gap, smallest
first, and catalog files are grouped by source.

Look at one conjecture: [`cb-0043`](problems/conjectures/cb-0043.json).

Load all 14,865 records as one flat JSONL stream:

```bash
python3 scripts/export_records.py > problems.jsonl
```

Reading and exporting the data uses only the Python standard library.

## Layout

```text
problems/
  conjectures/       one JSON file per curated conjecture
  families/          six sourced problem families
  extended-catalog/  problem statements from published collections
  tables/            browse spreadsheets
  schemas/           the JSON contract for every record type

scripts/             validation, browse-table, and export tools
tests/               the test suite
```

## Problems can get solved

Every open-status record is tied to a date or pinned source revision. When the
Kourovka Notebook reports an answer, the record remains available with status
`reported-answered-by-source`. This records the source's report; it is not our
verification. Git history and releases preserve earlier versions.

## Validate the repository

```bash
python3 -m pip install -r requirements-dev.txt

python3 scripts/validate_records.py
python3 scripts/build_browse_tables.py --check
python3 -m pytest -q
```

Continuous integration runs these checks. Reading the data itself needs
nothing installed.

## Source standard

Preferred evidence is an original paper, peer-reviewed survey, recent primary
preprint, expert-maintained problem list, or institutional page. Secondary
aggregations can supply catalog records but do not independently establish
current status. Every open-status record is attributed and tied to a date or
pinned source revision; unresolved extraction or status conflicts remain
explicit in the record.

## Contributing

Current intake is intentionally narrow: claimed results for existing problem
IDs use the claimed-result issue form; source-backed corrections use pull
requests. We are not accepting new problems, checkers, or broad format
changes. See [CONTRIBUTING.md](CONTRIBUTING.md).

Cataloguing a claim records who made it and where its evidence can be found; it
is not mathematical verification or endorsement by the maintainers. Browse
[catalogued claims](https://github.com/bespokelabsai/conjecture-bench/issues?q=is%3Aissue+is%3Aclosed+label%3Acatalogued-claim).

## License

The code is licensed under [Apache-2.0](LICENSE). The records, tables, and
documentation that Bespoke Labs created are licensed under
[CC BY 4.0](LICENSE-DATA). Problem content reproduced from upstream
collections remains its authors' work; [NOTICE](NOTICE) lists every source,
its terms, and what this repository holds from it.

## Citation

```bibtex
@misc{conjecturebench2026,
  title  = {ConjectureBench: a curated collection of open mathematics problems},
  author = {Ramesh, Anirudha and Pimpalgaonkar, Shreyas},
  year   = {2026},
  note   = {Bespoke Labs},
  url    = {https://github.com/bespokelabsai/conjecture-bench}
}
```

Please also cite the collections the problems come from. Each `source.json`
under [`problems/families/`](problems/families) records how
its maintainers ask to be cited, every extended-catalog record names its
source, and every curated conjecture stores its source links in
`provenance.sources`.

## Further reading

- [`problems/tables/README.md`](problems/tables/README.md), how to read the tables
- [`problems/schemas/README.md`](problems/schemas/README.md), which schema covers which record
