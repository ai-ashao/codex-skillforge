# site-opportunity-scorecard

A reusable Codex/ChatGPT Agent Skill for deciding whether an SEO product opportunity should become:

- an independent website;
- a section of an existing website;
- a single landing/tool page;
- or be observed/rejected.

## Install for Codex

Copy the folder to the user-level skill directory:

```bash
mkdir -p ~/.codex/skills
cp -R site-opportunity-scorecard ~/.codex/skills/
```

Codex detects changes automatically. Restart Codex if the skill does not appear.

For a repository-local installation:

```bash
mkdir -p .codex/skills
cp -R site-opportunity-scorecard .codex/skills/
```

## Invoke

In Codex CLI or the IDE extension:

```text
$site-opportunity-scorecard
```

Example prompt:

```text
Use site-opportunity-scorecard to evaluate whether "markdown to image" should be
an independent site or a section of mdformats.com. Target market: global English.
Business model: AdSense. Constraints: browser-side processing, low maintenance,
no login. Compare the current leading competitors and produce the full scorecard.
```

## Optional deterministic scoring

```bash
python3 scripts/calculate_score.py assets/assessment-input-template.json
```

Validate a generated Markdown report:

```bash
python3 scripts/validate_report.py --lang auto report.md
```

`--lang auto` supports the included Chinese and English report templates. For
structured scores, model hard gates as `{ "reason": "...", "scope": "SITE_ONLY" }`
or `{ "reason": "...", "scope": "BLOCK_PRODUCT" }`; the latter prevents every
architecture recommendation until the blocker is resolved.
