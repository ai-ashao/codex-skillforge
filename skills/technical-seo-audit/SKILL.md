---
name: technical-seo-audit
description: Run an evidence-led technical SEO audit of a public URL using bounded, SSRF-aware deterministic checks for HTTP delivery, indexability signals, robots.txt, sitemaps, canonical URLs, page metadata, headings, links, images, and JSON-LD. Use when a user asks for a technical SEO audit, on-page SEO check, crawlability review, metadata/schema check, or a reproducible URL audit. Use website-audit-scorecard separately for product, UX, trust, monetization, or overall quality scoring. Do not use this skill to make ranking, traffic, or keyword-demand claims without independent Search Console, SERP, or keyword evidence.
---

# Technical SEO Audit

Use deterministic scripts for observable facts and reserve semantic conclusions for clearly labelled review. A missing public signal is not automatically a defect.

## Core rules

- Audit the current URL, redirect target, and retrieved static HTML. Record any rendering, access, or data limitation.
- Do not present a title length, description length, word count, H1 count, heading count, or keyword position as a universal pass/fail rule. Treat it as context for review.
- Do not infer a target keyword from page copy and then score the page against that inference. Use a user-supplied query when available; otherwise mark intent alignment unassessed.
- Do not claim indexation, rankings, traffic, Core Web Vitals field data, crawl coverage, or Google Search Console status from a public HTML fetch.
- Treat `noindex`, a crawler-blocking robots rule, broken canonicalization, malformed JSON-LD, and retrieval failure as evidence to investigate. Confirm intentional exceptions with the user.
- Use only original/current evidence. Do not rely on a cached audit or a competitor’s marketing claims.

## Safe retrieval boundary

Run the bundled scripts only against public HTTP(S) URLs. `scripts/url_safety.py` rejects private, loopback, link-local, multicast, reserved, and non-standard-port targets, checks every redirect target, caps redirects and response bytes, and never sends credentials.

This is a harm-reduction layer, not a complete network-security boundary: DNS can change after validation. Run untrusted URL audits in an environment with outbound network controls; do not repurpose these scripts as a privileged internal-network fetcher.

## Workflow

### 1. Establish scope

Record the requested URL, production/staging status, whether the page is expected to be indexable, target country/language, and any supplied target query. Mark missing GSC, server logs, rendering access, and PageSpeed/CrUX data as unavailable rather than guessing.

### 2. Run deterministic checks

From this skill directory, run:

```bash
python3 -B scripts/check_site.py https://example.com
python3 -B scripts/check_page.py https://example.com/page --keyword "user-supplied query" --expected-indexable
```

Both scripts output JSON to stdout and do not create or modify the target site. `check_page.py` reports static-HTML limitations. `check_site.py` reads only the supplied origin’s `robots.txt` and discovered/default sitemap; it does not crawl an entire site.

### 3. Interpret only what the evidence supports

Read `references/evidence-and-interpretation.md` before assigning priority. Separate:

- `OBSERVED`: a script result or directly inspected response;
- `REVIEW`: a human/LLM judgement needed for intent, copy, architecture, or an intentional exception;
- `UNASSESSED`: unavailable without a browser, GSC, logs, source code, or other supplied evidence.

For semantic search-intent work, require a user query, real Search Console data, or live SERP evidence. For rendered DOM, interaction, visual layout, or Core Web Vitals, use the relevant browser/performance tools separately.

### 4. Produce the audit

Use `assets/report-template.md`. Include the JSON evidence, impact, exact remediation, owner/next check, and evidence limit for every material finding. Use `P0` only for a confirmed release blocker such as an unintended public `noindex` or crawler-wide block; do not inflate advisory items.

### 5. Route adjacent work correctly

- Use `$website-audit-scorecard` for a scored product, UX, trust, AdSense, or release-readiness assessment.
- Use `$web-asset-pipeline` for image performance, responsive variants, and image-source rights.
- Use browser/network checks for JavaScript rendering, visual validation, and user-flow testing.

## Completion standard

A complete audit contains the target and conditions, raw script outputs or cited observations, evidence classification, prioritized findings, explicit unassessed areas, and a re-check method. It never turns generic SEO folklore into a verified defect.
