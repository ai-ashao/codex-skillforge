---
name: site-opportunity-scorecard
description: Evaluate whether an SEO keyword cluster, product feature, competitor-derived idea, or existing site section should become an independent website, remain a section, remain a single landing page, or be rejected. Use for tool-site selection, site splitting, SEO product positioning, homepage entry-point analysis, competitor opportunity analysis, and low-maintenance website portfolio decisions. Do not use as a general technical SEO audit of an already-built site.
---

# Site Opportunity Scorecard

Assess the correct site architecture for a keyword cluster or product opportunity. The output must make a decision, expose the evidence, and separate market opportunity from site-separation risk.

## Use this skill when

Use it when the user asks questions such as:

- Should this function become a separate website?
- Should I build site C against sites A and B?
- Is this keyword cluster large and distinct enough for a new domain?
- Should this idea be a homepage, a subdirectory, a tool page, or be abandoned?
- Which feature should be the homepage entry point?
- Can several sites reuse the same underlying features without becoming duplicate shells?
- Evaluate a tool-site, game-site, calculator, converter, downloader, viewer, generator, or niche content opportunity.

## Do not use this skill when

- The user only wants a technical SEO audit, accessibility audit, visual review, code review, or conversion-rate audit of an existing site.
- The task is only keyword research without an architecture decision.
- The user asks for traffic, revenue, or ranking estimates without enough evidence and does not want an opportunity assessment.

When both an existing-site audit and an opportunity decision are needed, complete the opportunity decision separately. Do not merge the two scores.

## Required decision

Always choose exactly one primary recommendation:

1. `INDEPENDENT_SITE`
2. `EXISTING_SITE_SECTION`
3. `EXISTING_SITE_PAGE`
4. `OBSERVE_OR_REJECT`

Do not end with only “worth considering.”

## Inputs

Use the information available. Typical inputs are:

- target feature, product idea, or keyword cluster;
- target country, language, and device context;
- existing site or portfolio that could host the feature;
- competitor sites A/B and their homepage positioning;
- business model, such as AdSense, affiliate, subscription, or lead generation;
- maintenance, API, database, compliance, and platform constraints;
- third-party keyword data supplied by the user;
- publicly observable SERPs and competitor pages.

If important data is missing, do not fabricate it. Continue with a provisional assessment, label missing fields, lower confidence, and provide a minimum validation plan.

## Workflow

### 1. Frame the candidate

Define:

- candidate product or feature;
- primary user task;
- proposed main keyword cluster;
- target market and language;
- possible host site, if any;
- business and maintenance constraints.

Distinguish the product concept from the keyword. A product name is not automatically a validated keyword.

### 2. Build the keyword cluster

Group only terms that resolve to substantially the same user task. Use these buckets when relevant:

- primary functional terms;
- close synonyms and input/output variants;
- scenario and audience terms;
- problem/solution terms;
- comparison and alternative terms;
- template, example, guide, and specification terms;
- country and language variants.

Do not inflate the cluster with unrelated high-volume terms or mechanically swapped pages.

### 3. Inspect the SERP and competitors

When browsing is available, inspect the live SERP and actual competitor pages. Determine:

- whether ranking results are homepages, dedicated tools, broad suites, forums, documentation, videos, or marketplaces;
- how many results directly satisfy the tool intent;
- whether weak, outdated, thin, broken, slow, or poorly localized pages rank;
- whether large brands dominate because of authority rather than product fit;
- whether the candidate can win through a better workflow, output, audience focus, language, privacy model, speed, or content system;
- whether the SERP is unstable or driven by a temporary trend.

Follow `references/serp-analysis-rules.md`.

### 4. Compare product positioning

Compare sites A, B, and candidate C across:

- target user;
- primary job-to-be-done;
- homepage workflow;
- default input and output;
- core promise;
- differentiating capability;
- content system;
- share/link reason;
- monetization and maintenance model.

Classify differentiation as `NONE`, `COSMETIC`, `MODERATE`, or `STRONG` using `references/differentiation-rules.md`.

### 5. Score opportunity

Score every opportunity criterion from 0 to 5. Calculate the weighted score using `references/scoring-rubric.md`.

Opportunity dimensions total 100 points:

- Search opportunity: 39
- Product differentiation: 32
- Independent growth: 19
- Site economics: 10

Use `scripts/calculate_score.py` when structured scores are available.

### 6. Score separation risk

Score every risk criterion from 0 to 5, where 5 means highest risk. Calculate a separate 0–100 risk score.

Never hide a high separation risk inside the opportunity score.

### 7. Check hard gates

Do not recommend `INDEPENDENT_SITE` when any hard gate applies:

- no clear independent primary keyword or discoverable demand;
- primary demand is mainly a third-party brand navigation query;
- candidate and host site resolve to the same user intent with no meaningful workflow difference;
- the only differences are logo, color, domain, wording, or feature-card order;
- no credible independent page or content expansion beyond near-duplicate variants;
- unacceptable copyright, legal, platform, or policy dependency;
- maintenance or service burden violates the stated operating constraints;
- evidence quality is too low to justify a new domain without validation.

Classify every hard gate before scoring:

- `SITE_ONLY`: blocks a new domain, but a section or page on an existing site may remain viable. Use for overlap, insufficient independent demand, or insufficient evidence for a new domain.
- `BLOCK_PRODUCT`: blocks every architecture until resolved. Use for unacceptable copyright, legal, platform, policy, or maintenance constraints.

In structured input, represent a hard gate as `{ "reason": "...", "scope": "SITE_ONLY" | "BLOCK_PRODUCT" }`. Legacy string entries are treated as `SITE_ONLY`; do not use them for legal, policy, or operational blockers.

### 8. Choose architecture

Apply `references/architecture-decision.md`. Use score thresholds as guardrails, not as a substitute for judgment.

The recommendation must explain:

- why this architecture is superior to the alternatives;
- which evidence is decisive;
- what would change the decision;
- whether the candidate should be tested on an existing domain first.

### 9. Produce the report

Use `references/report-template.md`. Match the user’s language. For Chinese users, write the report in Simplified Chinese unless requested otherwise.

Every scored criterion must include:

- raw score;
- weighted score;
- evidence;
- evidence type;
- confidence.

Clearly distinguish:

- verified first-party data;
- supplied third-party metrics;
- live public-page observations;
- model inference;
- missing data.

Follow `references/evidence-confidence.md`.

## Scoring discipline

- A 3 means adequate evidence, not “unknown.”
- Unknown data is not a neutral 3. Mark it missing and lower confidence.
- Do not award high SERP scores solely because KD is low.
- Do not award high long-tail scores to thin permutations.
- Do not award high brand scores for a possible domain name alone.
- Do not award high external-link scores without naming plausible linkers, reasons, and target assets.
- Do not recommend a new site only because code can be reused.
- Do not treat CPC 0 as proof of no value; assess intent, geography, monetization, and data quality.

## Minimum validation plan

When confidence is medium or low, include a test that can be completed before buying or fully developing a new domain. Prefer one or more of:

- publish a dedicated page or section on the existing domain;
- monitor impressions, ranking breadth, CTR, and tool completions;
- run a lightweight exact-match landing page without duplicating the full site;
- collect Bing/GSC query data;
- inspect 30/90-day trend stability;
- test shareability or link outreach with a real asset;
- build a browser-only prototype to validate workflow differentiation;
- interview or observe users only when the project economics justify it.

Define success thresholds and a re-evaluation trigger.

## Supporting files

Load these when needed:

- `references/scoring-rubric.md`: criteria, weights, and score anchors.
- `references/evidence-confidence.md`: evidence labels and confidence method.
- `references/serp-analysis-rules.md`: SERP inspection and weakness classification.
- `references/differentiation-rules.md`: genuine versus cosmetic differentiation.
- `references/architecture-decision.md`: page/section/site decision logic.
- `references/report-template.md`: required Simplified Chinese final report format.
- `references/report-template-en.md`: required English final report format.
- `references/examples.md`: worked examples and anti-patterns.
- `assets/assessment-input-template.json`: optional structured input.
- `scripts/calculate_score.py`: deterministic scoring and preliminary recommendation.
- `scripts/validate_report.py`: report completeness validation.

## Completion standard

A complete assessment must contain:

- opportunity score out of 100;
- separation risk out of 100;
- evidence confidence;
- exactly one architecture recommendation;
- score breakdown with evidence;
- keyword-cluster assessment;
- SERP entry point;
- A/B/C positioning comparison when competitors are available;
- proposed homepage entry point when relevant;
- MVP page matrix;
- independent linking/distribution logic;
- key risks and hard gates;
- minimum validation plan and re-evaluation conditions.
