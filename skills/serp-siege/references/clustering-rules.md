# Intent-first Clustering Rules

## Cluster order

Group candidates in this order:

1. search intent;
2. primary user task;
3. input and output;
4. meaningful constraint;
5. SERP similarity;
6. workflow difference.

String similarity is supporting evidence, not the primary rule.

## Cluster types

Use only applicable types:

- `CORE`
- `FORMAT`
- `CONSTRAINT`
- `USE_CASE`
- `AUDIENCE`
- `PLATFORM`
- `ADJACENT_TOOL`
- `CONTENT_SUPPORT`

Every cluster needs a stable name, one primary keyword, one user intent, supporting queries, evidence, and a proposed page treatment.

## Parent and child behavior

- Merge synonyms and word-order variants into the same cluster.
- Keep a format child separate only when file behavior, output expectation, or SERP intent materially differs.
- Keep a constraint child separate only when the constraint changes the tool controls, validation, output, or recurring SERP composition.
- Treat an adjacent tool as a new cluster when it solves a different primary task, even if it shares the same processing core.
- Use `CONTENT_SUPPORT` when the dominant intent is explanatory and a tool page alone would not satisfy it.

## Cannibalization test

Prefer one page when the candidate pages would have substantially the same:

- primary task and promise;
- input and output workflow;
- SERP result set;
- page content and controls;
- internal-link destination.

Create separate pages only when at least one of those dimensions changes materially and the evidence is named.

## Thin permutation rejection

Reject mechanical variations based only on:

- a swapped number or unit;
- a country name without real localization or rules;
- `free`, `online`, `best`, or `no signup` wording;
- singular/plural, spelling, or word order;
- format labels when the workflow and SERP are effectively identical.

Do not discard rejected candidates silently. Record the parent cluster and rejection reason in the SEO Page Map. Rejecting a page does not reject the project.
