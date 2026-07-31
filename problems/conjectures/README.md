# Curated conjectures

Each `cb-NNNN.json` file is one individually curated conjecture. It stores the
statement, what a counterexample would be, a dated status observation, and
source links. The file is the source of truth.

## Files

- `cb-NNNN.json`, one conjecture each; the contract is
  [`../schemas/conjecture.schema.json`](../schemas/conjecture.schema.json)

The collection holds 302 conjectures. Equivalent formulations may share an
`equivalence_group`; an exact duplicate uses `duplicate_of`.

## Status

`open` is always a dated observation, never a permanent label. A disputed
status is recorded as `status-contested` with a source-backed note. Git history
preserves prior versions.
