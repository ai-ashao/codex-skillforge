# Audit Report Template

# [Site] Audit

## Verdict

- Final score: **X/100**
- Raw score: **X/100**
- Coverage: **X%**
- Evidence confidence: **X%**
- Status: mature / viable / functional but immature / risky / not ready
- Audit label: final / provisional / not scorable

One paragraph explaining the dominant strength, dominant weakness, and next milestone.

## Score breakdown

| Category | Score | Available | Coverage | Main reason |
|---|---:|---:|---:|---|
| Product and value | | 15 | | |
| Core task and UX | | 20 | | |
| Trust/safety/compliance | | 15 | | |
| SEO/indexability | | 15 | | |
| Content/originality | | 10 | | |
| Performance/accessibility | | 10 | | |
| Technical reliability | | 10 | | |
| Monetization readiness | | 5 | | |

## Critical gates

List triggered gates and caps. Write `None` when no gate was triggered.

## Highest-priority findings

For each P0/P1 finding include:

- criterion ID;
- observed evidence;
- impact;
- required fix;
- acceptance check.

## What is working

List only evidence-backed strengths.

## Evidence limitations

State what was not accessed or tested. Do not hide limited coverage.

## Next plan

Separate:

1. immediate hotfix;
2. next product milestone;
3. SEO/content track;
4. monetization gate;
5. deferred work.

## Re-audit delta

For re-audits:

| Criterion | Previous | Current | Delta | Evidence | Status |
|---|---:|---:|---:|---|---|
| | | | | | fixed / partial / unchanged / regression |
