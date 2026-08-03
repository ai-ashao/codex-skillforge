---
name: website-audit-scorecard
description: Audit and score a live website or web product with a reproducible 100-point rubric, evidence grades, coverage, confidence, critical gates, regression comparison, and prioritized remediation plan. Use when the user asks for a full website audit, re-audit after deployment, product/UX/SEO/AdSense readiness review, score explanation, before-vs-after comparison, or a Codex-ready implementation plan for an SEO tool site, content site, downloader, converter, viewer, generator, or lightweight SaaS.
---

# Website Audit Scorecard

Use this workflow to produce evidence-based, repeatable website audits. Never invent precision from incomplete access.

## Core rules

1. Inspect the current deployment, not memory or an earlier crawl.
2. Separate **score**, **coverage**, and **confidence**.
3. Tie every deduction to observable evidence.
4. Do not score an untested criterion as zero. Mark it `unassessed`.
5. Apply transparent critical gates after calculating the raw score.
6. Do not describe this rubric as an official Google, Lighthouse, WCAG, or AdSense score.
7. For re-audits, use the same rubric and show criterion-level deltas.
8. When the user asks for implementation, audit first; then generate a scoped plan.

## Required resources

Read:

- `references/rubric.md` for criteria, weights, anchors, gates, and bands.
- `references/evidence.md` for evidence grades and coverage/confidence calculation.
- `references/report-template.md` for the final output structure.

Use `scripts/calculate_score.py` for deterministic calculation.

## Workflow

### 1. Define the audit target

Record:

- Canonical URL and deployment URL, if different.
- Site type: `seo-tool`, `content`, `saas`, or `generic`.
- Primary user task.
- Audit mode: `baseline`, `re-audit`, or `release-gate`.
- Surfaces in scope: desktop, mobile, public routes, core task, result states, SEO files, source repository.

Default to `seo-tool` for downloaders, converters, generators, viewers, calculators, and browser utilities monetized mainly by ads.

### 2. Establish evidence

Prefer evidence in this order:

1. Live interaction and network/DOM inspection.
2. Current source code and deployment metadata.
3. Current rendered HTML and HTTP responses.
4. Current screenshots.
5. Search snippets or cached pages only as supporting evidence.

Do not claim a full interaction audit when only static HTML was accessible.

### 3. Audit the rubric

Score each criterion from 0 to 4:

- `0`: absent, broken, materially misleading, or unusable.
- `1`: weak; serious gaps.
- `2`: acceptable baseline; functional but incomplete.
- `3`: good; minor gaps.
- `4`: strong; complete and well executed.

Use only integer ratings. Add:

- evidence grade: `A`, `B`, `C`, or `U`;
- concise evidence note;
- source URL, route, screenshot, code path, or test identifier.

Mark a criterion `unassessed` when evidence is insufficient.

### 4. Calculate deterministically

Create a JSON input using the schema documented in `references/evidence.md`, then run:

```bash
python scripts/calculate_score.py audit.json
```

Report:

- raw normalized score;
- final score after critical gates;
- assessed coverage;
- evidence confidence;
- category scores;
- triggered gates.

A score with coverage below 70% must be labeled **provisional**.
Coverage below 40% is **not scorable**.

### 5. Prioritize findings

Classify findings:

- `P0`: blocks the core task, creates material deception/security risk, or invalidates production.
- `P1`: materially harms conversion, SEO, trust, accessibility, or reliability.
- `P2`: meaningful quality improvement.
- `P3`: polish or optional optimization.

Do not turn every deduction into a P0.

### 6. Produce a remediation plan

Group work into:

- immediate hotfix;
- next product milestone;
- SEO/content track;
- monetization gate;
- deferred items.

For Codex plans, state:

- immutable product decisions;
- in scope;
- out of scope;
- file-level inspection required before coding;
- tests;
- acceptance criteria;
- branch/PR sequence.

### 7. Re-audit

For a re-audit:

1. Re-capture current evidence.
2. Re-score every assessed criterion.
3. Compare against the saved baseline.
4. Show score delta by category and criterion.
5. Distinguish:
   - fixed;
   - partially fixed;
   - unchanged;
   - regression;
   - newly unassessed.
6. Never increase a score only because code was changed; verify deployment behavior.

## Output requirements

Always include:

- overall verdict;
- final score, raw score, coverage, and confidence;
- score breakdown;
- triggered gates;
- top P0/P1 findings;
- evidence limitations;
- next milestone;
- for re-audits, a delta table.

Do not present a single number without its calculation basis.
