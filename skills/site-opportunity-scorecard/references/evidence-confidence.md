# Evidence and Confidence

Every important claim and score should identify its evidence type.

## Evidence labels

Use one or more of these labels:

- `FIRST_PARTY`: Search Console, Bing Webmaster Tools, analytics, revenue, conversion, user behavior, support logs, or experiments owned by the user.
- `USER_SUPPLIED_THIRD_PARTY`: Ahrefs, Semrush, Similarweb, Keyword Planner, app-market data, or screenshots supplied by the user.
- `LIVE_PUBLIC_OBSERVATION`: Current SERP, competitor page, sitemap, pricing page, product workflow, public repository, public policy, or public traffic surface inspected directly.
- `HISTORICAL_PUBLIC_SOURCE`: A dated article, archive, case study, report, or older snapshot.
- `MODEL_INFERENCE`: Reasoned inference from observed facts.
- `MISSING`: Required evidence not available.

Never present model inference as measured data.

## Criterion confidence

Assign `HIGH`, `MEDIUM`, or `LOW` to each scored criterion.

### HIGH

Use when the score is supported by strong first-party data or multiple current, directly relevant observations. Examples:

- GSC queries plus live SERP inspection;
- actual conversion/completion data;
- current competitor workflow plus supplied Ahrefs metrics;
- repeated trend data across meaningful time windows.

### MEDIUM

Use when the score is supported by live public observations or one credible third-party source, but lacks first-party validation.

### LOW

Use when evidence is missing, stale, indirect, inferred, or based on a single ambiguous signal.

## Overall confidence

Calculate overall confidence qualitatively:

- `HIGH`: At least 7 of 10 opportunity criteria are high confidence, no decision-critical criterion is low, and live SERP evidence is available.
- `MEDIUM`: At least 6 criteria are medium or high, with no more than two decision-critical low-confidence items.
- `LOW`: Three or more decision-critical criteria are low, live SERP evidence is unavailable, or primary demand is unverified.

Decision-critical criteria are:

- independent primary keyword;
- SERP breakability;
- user/use-case difference;
- homepage workflow difference;
- link/distribution potential.

## Missing data behavior

Do not use a raw score of 3 as a placeholder for missing data.

When a criterion is missing:

1. make the best bounded provisional score only if there is indirect evidence;
2. label the evidence `MISSING` plus `MODEL_INFERENCE`;
3. set confidence `LOW`;
4. state what data would change the score;
5. avoid an irreversible independent-site recommendation unless the remaining evidence is exceptionally strong.
