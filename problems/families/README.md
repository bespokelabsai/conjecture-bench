# Problem families

9,342 unsolved problems in six families. A family is a set of problems that
share a mathematical form and source.

| Family | Problems | What an answer is |
| --- | ---: | --- |
| ljcr-covering-designs | 1,480 | a smaller covering than the best known |
| codetables-linear-codes | 965 | a binary code better than the best known |
| codetables-nonbinary-linear-codes | 3,535 | a code over GF(3) to GF(9) better than the best known |
| ljcr-difference-sets | 3,064 | a difference set whose existence is open |
| brouwer-constant-weight-codes | 250 | a larger constant weight code than the best known |
| small-ramsey-numbers | 48 | a coloring that raises a Ramsey lower bound |

Every problem is unsolved. A problem is recorded only while its published
bounds disagree, or while its existence question is open. Five families record
the gap between their published bounds. Gaps are only comparable within one
family. See
[`../tables/README.md`](../tables/README.md).

## Layout

```text
families/<name>/
  records.json     the problems
  source.json      who compiled the source data and how to cite them
```

## Where the problems come from

Each family is built from one published collection, named and credited in its
`source.json`, including how the maintainers ask to be cited. Every record
stores the address of the page it came from and a quote from that page. The
optional `frontier` block records published bounds or the current goal.

## Contributions

New families and problem sources are not currently accepted. See the root
[`CONTRIBUTING.md`](../../CONTRIBUTING.md).
