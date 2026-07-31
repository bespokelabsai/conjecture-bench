# Contributing

ConjectureBench currently accepts only:

1. a claimed solution or improved result for an existing problem ID; or
2. a factual correction to an existing record, supported by a reliable source.

We are not accepting new problems, new collections, checkers, benchmark
adapters, or general rewrites. Keeping intake narrow limits maintenance and
avoids implying review that we cannot provide.

## Claimed results

Open a
[claimed-result issue](https://github.com/bespokelabsai/conjecture-bench/issues/new?template=claimed-result.yml).
GitHub assigns the claim ID as `CC-CLAIM-<issue number>`. The form records the
problem ID, claimant names, any model and exact version used, a durable result
artifact, and available external validation. No pull request or repository
file is required.

Maintainers check that the problem ID exists, the links work, the metadata is
complete, and the claim is not an obvious duplicate. We do not check proofs,
run witnesses, certify priority, or endorse mathematical correctness. A claim
must remain labelled as a claim unless its status is supported by an external
publication or independent review.

After this metadata check, maintainers apply the `catalogued-claim` label and
close the issue as recorded. Closing means catalogued, not mathematically
verified. [Browse catalogued claims](https://github.com/bespokelabsai/conjecture-bench/issues?q=is%3Aissue+is%3Aclosed+label%3Acatalogued-claim).

## Corrections

Identify the affected problem ID and cite the source supporting the correction.
Update the authoritative record, then regenerate the browse tables with
`python3 scripts/build_browse_tables.py`. Do not edit generated CSV files by
hand. Corrections use pull requests; claimed results do not.

## Not accepted currently

- new problems or collections;
- checker or verifier implementations;
- formalizations unrelated to an existing claimed result;
- difficulty ratings, model scores, or leaderboard additions.

Pull requests outside this scope may be closed without detailed review.
