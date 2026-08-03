# Reproducible 100-Point Rubric

## Table of contents

1. Scoring model
2. Categories and criteria
3. Rating anchors
4. Critical gates
5. Score bands
6. Site-type interpretation

## 1. Scoring model

Each criterion has a fixed maximum point value and an integer rating from 0 to 4.

```text
criterion_points = max_points × rating ÷ 4
```

For assessed criteria:

```text
raw_score = earned_points ÷ assessed_max_points × 100
coverage = assessed_max_points ÷ 100 × 100
```

Apply critical gates after calculating the raw score:

```text
final_score = min(raw_score, lowest_triggered_cap)
```

Do not round individual criteria. Round category and overall scores to one decimal place.

## 2. Categories and criteria

### A. Product and value proposition — 15 points

| ID | Criterion | Max |
|---|---|---:|
| PV1 | Search/user intent is immediately clear | 4 |
| PV2 | Claimed value matches actual capability | 4 |
| PV3 | Differentiation is concrete and user-visible | 3 |
| PV4 | Scope and technical limitations are clear | 2 |
| PV5 | User knows the next action and expected outcome | 2 |

### B. Core task and UX — 20 points

| ID | Criterion | Max |
|---|---|---:|
| UX1 | Primary action is obvious and low-friction | 3 |
| UX2 | Input requirements and validation are clear | 3 |
| UX3 | Loading/progress states prevent confusion and duplicate actions | 2 |
| UX4 | Success states expose the right information and next action | 4 |
| UX5 | Failure/empty/restricted states explain recovery | 4 |
| UX6 | Mobile and keyboard use are practical | 2 |
| UX7 | Retry, navigation, and task continuity are preserved | 2 |

### C. Trust, safety, and compliance — 15 points

| ID | Criterion | Max |
|---|---|---:|
| TS1 | Claims are truthful and not materially misleading | 4 |
| TS2 | Data handling and privacy are transparent | 3 |
| TS3 | Relevant safety risks and limitations are disclosed | 3 |
| TS4 | Contact, legal, copyright, and ownership information are usable | 3 |
| TS5 | Brand, navigation, and policy language are consistent | 2 |

### D. SEO and indexability — 15 points

| ID | Criterion | Max |
|---|---|---:|
| SEO1 | Titles, descriptions, canonicals, and language metadata are correct | 3 |
| SEO2 | Robots, sitemap, status codes, and index controls are correct | 3 |
| SEO3 | Information architecture and internal linking support discovery | 3 |
| SEO4 | Pages satisfy distinct search intent and avoid thin duplication | 3 |
| SEO5 | Structured data, social metadata, and localization signals are appropriate | 3 |

### E. Content and originality — 10 points

| ID | Criterion | Max |
|---|---|---:|
| CO1 | Content solves real user questions beyond generic copy | 4 |
| CO2 | Topic depth matches the query and product complexity | 2 |
| CO3 | Original tests, data, examples, or expert evidence are present | 2 |
| CO4 | Freshness, ownership, and maintenance signals are credible | 2 |

### F. Performance and accessibility — 10 points

| ID | Criterion | Max |
|---|---|---:|
| PA1 | Core Web Vitals and loading performance are acceptable | 4 |
| PA2 | Semantic HTML, labels, focus, contrast, and announcements are usable | 3 |
| PA3 | Responsive layouts avoid overflow and unusable targets | 2 |
| PA4 | Layout stability, image fallback, and visual error handling are sound | 1 |

### G. Technical reliability — 10 points

| ID | Criterion | Max |
|---|---|---:|
| TR1 | Public routes, assets, and navigation are healthy | 2 |
| TR2 | API/network failures, timeouts, retries, and rate limits are handled | 3 |
| TR3 | Inputs, redirects, external URLs, and secrets are safely validated | 2 |
| TR4 | Tests, analytics, logging, and diagnostics cover the core flow | 2 |
| TR5 | Production deployment matches the reviewed commit/version | 1 |

### H. Monetization readiness — 5 points

| ID | Criterion | Max |
|---|---|---:|
| MR1 | Site has sufficient original value and policy-ready content | 2 |
| MR2 | Ads cannot be confused with task, download, or navigation controls | 1 |
| MR3 | Ad density and placement preserve the primary user task | 1 |
| MR4 | Consent, privacy, and regional disclosure plans are ready | 1 |

Total: **100 points**

## 3. Rating anchors

### Rating 0

Use when the criterion is absent, broken, unsafe, materially misleading, or prevents task completion.

### Rating 1

Use when something exists but has major defects, weak coverage, or repeated inconsistency.

### Rating 2

Use for a working baseline with visible limitations. Do not call this “good.”

### Rating 3

Use when the implementation is solid and only minor issues remain.

### Rating 4

Use only when current evidence demonstrates complete, consistent, and strong execution.

Do not use half ratings. Precision comes from criterion weights, not decimal ratings.

## 4. Critical gates

Apply only when directly evidenced.

| Gate | Trigger | Score cap |
|---|---|---:|
| G0 | Site or primary surface cannot be accessed sufficiently to audit | Not scorable |
| G1 | Primary task is broken for normal valid input | 49 |
| G2 | Materially deceptive download/payment/security behavior | 39 |
| G3 | Exposed credentials, arbitrary command injection, or critical security flaw | 29 |
| G4 | Production serves a materially different/older build than the claimed release | 59 |
| G5 | Major legal or platform-policy blocker for the stated monetization model | Monetization status: Not ready; no overall cap |

A gate is not a substitute for criterion deductions. Report both.

## 5. Score bands

| Score | Interpretation |
|---:|---|
| 90–100 | Strong, mature, and release-ready |
| 80–89 | Good; limited high-impact gaps |
| 70–79 | Viable; important improvements remain |
| 60–69 | Functional but immature |
| 50–59 | Risky; core quality gaps |
| 30–49 | Not ready for growth or monetization |
| 0–29 | Critically broken or unsafe |

Add labels:

- `provisional` when coverage is 40–69.9%;
- `not scorable` when coverage is below 40%;
- `low confidence` when confidence is below 50%.

## 6. Site-type interpretation

### SEO tool site

Prioritize the core task, truthful capability, index controls, original utility, game/format-specific pages, and ad/download separation.

### Content site

Prioritize content originality, topical completeness, author/evidence signals, internal linking, and sustainable page quality.

### SaaS

Prioritize onboarding, activation, account/payment flows, reliability, support, privacy, and recurring value.

The weights remain fixed across site types to preserve comparability. Change the evidence emphasis, not the point totals.
