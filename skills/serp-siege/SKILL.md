---
name: serp-siege
description: Turn a user-selected tool-site competitor, website, or keyword into evidence-labeled coverage maps, a bounded first batch, and an MVP/P1/P2 execution roadmap. Use after the user has decided to pursue the direction; do not use to judge whether the project is worth doing, choose site architecture, build the site, publish pages, or monitor GSC.
---

# SERP Siege

Convert a competitor domain, website, keyword, or combination into a bounded product-and-SEO execution roadmap. Treat the user's request as a decision to proceed. Treat the competitor as a starting dataset, not a blueprint. Enumerate broadly, cluster by user intent, and recommend only pages backed by distinct tasks and reusable product capabilities.

## Responsibility boundary

This skill improves how to execute an already-selected direction. It must not:

- decide whether the project is worth doing;
- output `GO`, `CONDITIONAL_GO`, or `NO_GO`;
- calculate opportunity or separation-risk scores;
- choose between an independent site, existing-site section, or existing-site page;
- invoke an opportunity-analysis skill automatically;
- stop the roadmap merely because competition is strong or evidence is incomplete.

It may reject a proposed page, merge duplicate clusters, defer a feature, narrow the First Batch, or require an implementation prerequisite. Those are execution decisions, not project-admission decisions.

## Inputs

Accept either `target.domain`, `target.keyword`, or both. Also use these when supplied:

- `market.country` and `market.language`;
- `business.monetization` and `business.maintenance_preference`;
- `existing_site.domain`;
- `execution.destination` when the user has already chosen a site, section, or page;
- optional `opportunity_context` supplied from an upstream analysis.

Do not block on missing optional context or a missing opportunity report. State bounded assumptions, mark missing execution evidence, and lower planning confidence. Never invent search volume, keyword difficulty, traffic, revenue, CPC, or backlinks.

If upstream opportunity or architecture context is supplied, read [references/optional-handoff.md](references/optional-handoff.md). Consume it without rerunning or challenging the upstream decision.

## Workflow

1. **FRAME — set the filling.** Convert the user's selected direction into an execution frame: primary job, scope, destination if supplied, constraints, assumptions, and missing execution evidence.
2. **EXPAND — roll the wrappers.** Collect query and competitor dimensions with recall favored over precision. Use the bounded research rules in [references/dumpling-sop.md](references/dumpling-sop.md).
3. **CLUSTER — portion the filling.** Group by intent, task, input/output, constraint, SERP similarity, and workflow. Read [references/clustering-rules.md](references/clustering-rules.md).
4. **MAP — draw coverage.** Build the Feature Coverage Matrix and SERP Coverage Matrix using [references/coverage-model.md](references/coverage-model.md). Map clusters to page decisions with [references/page-mapping-rules.md](references/page-mapping-rules.md).
5. **PRIORITIZE — make the first batch.** Rank demand, SERP weakness, competitor validation, core reuse, expansion potential, build cost, and maintenance cost. Read [references/priority-rules.md](references/priority-rules.md).
6. **ROADMAP — write the menu.** Produce the applicable report from [references/report-template.md](references/report-template.md).

## Execution behavior

Continue through all six phases and produce an execution roadmap. When a serious platform, copyright, API, technical, or maintenance constraint appears:

- state which feature or page it affects;
- narrow, reorder, or condition the affected work;
- provide a safe or maintainable alternative where possible;
- identify the prerequisite or validation required before implementation;
- continue planning the unaffected scope.

Do not turn an execution constraint into a verdict on the whole project.

## Output rules

- Use exactly the evidence labels defined in the report template.
- One query is not one page. Reject thin number, country, wording, and format permutations unless intent or workflow evidence justifies a distinct page.
- Every proposed page must bind to a named cluster and shared capability.
- `SAME_PAGE` must name its canonical parent; `REJECT` may omit its proposed URL but must name its canonical parent and state the execution reason.
- Every P0 item must state why it belongs now.
- P1 and P2 may be `NONE`; never invent roadmap items to fill a section.
- Keep the default First Batch to one core tool, 3–5 supporting entries, and 2–5 adjacent capabilities, normally 8–15 effective search entrances. Explain deviations.
- Product coverage and SEO coverage must describe one roadmap, not separate wish lists.
- Match the user's language; default to Simplified Chinese for Chinese requests while preserving the template's canonical machine-readable headings.

Validate a saved Markdown report with the bundled script resolved relative to this `SKILL.md`:

```bash
python3 <serp-siege-root>/scripts/validate_output.py path/to/report.md
```

The script checks structural and contractual invariants only. It cannot prove that public observations are current or that a metric is truthful.
