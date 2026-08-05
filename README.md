# Codex Skillforge

[简体中文](README.zh-CN.md)

[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/ai-ashao/codex-skillforge?style=flat-square)](https://github.com/ai-ashao/codex-skillforge/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/ai-ashao/codex-skillforge?style=flat-square)](https://github.com/ai-ashao/codex-skillforge/forks)
[![Last commit](https://img.shields.io/github/last-commit/ai-ashao/codex-skillforge?style=flat-square)](https://github.com/ai-ashao/codex-skillforge/commits/main)

A maintained collection of custom Codex skills for evaluating and improving small web products. Each skill is self-contained: its `SKILL.md` describes when to use it, while bundled references, scripts, and fixtures make the result reproducible.

## Included skills

| Skill | Use it for | Deterministic support |
|---|---|---|
| [`site-opportunity-scorecard`](skills/site-opportunity-scorecard/) | Deciding whether an SEO keyword cluster or product feature should be an independent site, an existing-site section, a focused page, or rejected. | Weighted opportunity and separation-risk scoring, bilingual report templates, and report-structure validation. |
| [`website-audit-scorecard`](skills/website-audit-scorecard/) | Auditing a live site or web product for product quality, UX, trust, SEO, technical reliability, and monetization readiness. | Evidence-weighted coverage and confidence, critical gates, sample fixture, and regression tests. |
| [`web-asset-pipeline`](skills/web-asset-pipeline/) | Turning visual assets from AI, stock libraries, exports, or screenshots into production-ready web resources. | Non-mutating asset audit, asset-rights manifest template, format and framework integration guidance, and regression tests. |
| [`competitive-ui-reverse-engineering`](skills/competitive-ui-reverse-engineering/) | Turning competitor-page references and screenshots into differentiated page plans. | Evidence-aware UI decomposition, originality guardrails, reusable analysis template, and asset-pipeline handoff. |
| [`technical-seo-audit`](skills/technical-seo-audit/) | Auditing a multilingual public URL’s technical SEO signals without treating generic thresholds as defects. | Unified Markdown/JSON report, bounded SSRF-aware retrieval, delivery/indexability, robots/sitemaps, JSON-LD, hreflang, and 30+ regression tests. |

These are decision frameworks, not official Google, Lighthouse, WCAG, or AdSense scoring systems. Scores must always be accompanied by current evidence and coverage limits.

## Install a skill

Clone this repository, then copy only the skill you want into Codex's user-level skill directory:

```bash
git clone https://github.com/ai-ashao/codex-skillforge.git
mkdir -p ~/.codex/skills
cp -R codex-skillforge/skills/site-opportunity-scorecard ~/.codex/skills/
```

Replace `site-opportunity-scorecard` with the skill you need, such as `website-audit-scorecard`, `technical-seo-audit`, `web-asset-pipeline`, or `competitive-ui-reverse-engineering`. Start a new Codex turn after installation; restart Codex if it does not appear immediately.

## Use

Invoke a skill by name, then provide the target and constraints:

```text
Use $site-opportunity-scorecard to decide whether a Markdown-to-image workflow
should be an independent site or a section of an existing converter site.
```

```text
Use $website-audit-scorecard to audit https://example.com as a release gate.
```

```text
Use $web-asset-pipeline to audit, optimize, and integrate the visual assets for this website.
```

```text
Use $competitive-ui-reverse-engineering to analyze these competitor references and create a differentiated implementation plan.
```

```text
Use $technical-seo-audit to run a technical SEO audit for this URL and state the evidence limits.
```

Read each skill's `SKILL.md` for the required evidence, report format, and boundaries before relying on an assessment.

## Repository layout

```text
skills/
  <skill-name>/
    SKILL.md        # invocation rules and workflow
    references/     # rubric, evidence rules, and report templates
    scripts/        # deterministic helpers
    assets/         # sample inputs and expected results
    tests/          # regression tests when the skill includes executable logic
```

## Verify before publishing changes

Run the checks closest to the skill you changed:

```bash
python3 -B -m unittest discover -s skills/website-audit-scorecard/tests -v
python3 -B skills/site-opportunity-scorecard/scripts/calculate_score.py \
  skills/site-opportunity-scorecard/assets/assessment-input-template.json
python3 -B -m unittest discover -s skills/web-asset-pipeline/tests -v
python3 -B -m unittest discover -s skills/technical-seo-audit/tests -v
```

For a scorecard report, validate its structure and language profile:

```bash
python3 -B skills/site-opportunity-scorecard/scripts/validate_report.py \
  --lang auto path/to/report.md
```

## Maintenance conventions

- Keep scoring rules, calculators, templates, and samples in sync.
- Treat observed evidence, user-supplied metrics, and model inference as different evidence classes.
- Add a regression test whenever a calculator bug is fixed.
- Avoid putting credentials, production data, browser profiles, or user exports in this repository.
