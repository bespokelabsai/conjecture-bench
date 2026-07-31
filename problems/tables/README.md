# Tables

Spreadsheets covering every problem in this repository. Click a file on GitHub
and it appears as a table with a search box. The five family files with gaps
are sorted smallest first. Download the raw file for additional sorting or
filtering.

## What is in them

One row per problem. The columns tell you where the problem came from and, for
some families, how close the published bounds are.

A script writes these files from the problem records. Values are copied from
the records, and each gap is calculated by subtracting one published bound
from another.

Rebuild them with `python3 scripts/build_browse_tables.py`. Do not edit them by hand,
because the script overwrites them.

## Three kinds of problem record

The combined table uses three record kinds.

A `conjecture` is an individually curated conjecture in
`problems/conjectures/`. A `family` row is one instance of a sourced mathematical
family. A `catalog` row is a sourced entry in `problems/extended-catalog/`.

## The files

[`all.csv`](all.csv) lists all 14,865 records of all three kinds. It only has
columns that mean the same thing for every kind, so it has no gap column. It is
over a megabyte, so GitHub may decline to show it as a table. The smaller files
below are the ones to browse.

[`kind-conjecture.csv`](kind-conjecture.csv) lists the conjecture records.
The `catalog-<source>.csv` files list the extended catalog, one file per
source.

The remaining files each cover one family. Five include a gap column, with the
unit in its name, such as `gap_blocks`. The difference-set file has no gap
column.

## Columns

The combined, conjecture, and catalog tables use the first six columns below.
Family tables use `id`, `source`, `best_known`, and, where applicable, a gap
column.

| Column | Meaning |
| --- | --- |
| `id` | name of the problem, unique across the release |
| `kind` | `conjecture`, `family`, or `catalog` |
| `title` | the problem's title |
| `source` | which published collection it came from |
| `family` | the mathematical family a record belongs to, empty otherwise |
| `status` | the status recorded from the source |
| `best_known` | the current record to beat, family files only |
| `gap_*` | how far apart the best answer and the best proved limit are |

## Reading the gap

A `gap_*` column is the difference between the best published construction and
the best proved bound. Its unit appears in the column name. Compare gaps only
within the same file.
