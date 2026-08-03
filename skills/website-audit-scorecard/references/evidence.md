# Evidence, Coverage, and Calculator Input

## Evidence grades

| Grade | Meaning | Confidence multiplier |
|---|---|---:|
| A | Verified through current live interaction, network inspection, automated test, or current source plus deployment proof | 1.00 |
| B | Verified through current rendered page, HTTP response, DOM, metadata, or current source code | 0.85 |
| C | Supported only by a current screenshot, search snippet, cached page, or indirect evidence | 0.60 |
| U | Unverified or inaccessible | 0.00 |

Use the strongest evidence actually obtained. Do not upgrade evidence because a change was claimed.

## Coverage

Coverage measures how much of the 100-point rubric was assessed:

```text
coverage = assessed_max_points / 100 × 100
```

An `unassessed` criterion contributes nothing to assessed maximum points and nothing to earned points.

## Confidence

Confidence weights assessed coverage by evidence strength:

```text
confidence =
  sum(max_points × evidence_multiplier for assessed criteria) / 100 × 100
```

Confidence is not the probability that every finding is correct. It is a transparent evidence-strength indicator.

## JSON input schema

```json
{
  "audit": {
    "site": "https://example.com",
    "mode": "baseline",
    "profile": "seo-tool"
  },
  "ratings": {
    "PV1": {
      "rating": 3,
      "evidence": "B",
      "note": "The H1 and first screen identify the tool and supported input."
    },
    "UX4": {
      "rating": 2,
      "evidence": "A",
      "note": "Direct-link state works, but file size and source warnings are missing."
    },
    "PA1": {
      "status": "unassessed",
      "note": "No Lighthouse or field data was available."
    }
  },
  "gates": [
    {
      "id": "G4",
      "triggered": false,
      "note": "Production commit matched the reviewed deployment."
    }
  ]
}
```

Rules:

- `rating` must be an integer from 0 through 4. A criterion with neither a rating nor `"status": "unassessed"` is invalid input; it is never silently treated as unassessed.
- `evidence` must be `A`, `B`, or `C` for assessed criteria.
- Use `"status": "unassessed"` when evidence is insufficient; do not also include a rating or evidence grade.
- Include only known gate IDs `G0` through `G5`, at most once each, with a boolean `triggered` value. Omitted gates are treated as not triggered.
- `G0` returns `not scorable`.
- `G5` sets monetization status to `not ready` but does not cap the overall score. With no assessed monetization criterion and no G5, monetization status is `unassessed`.

## Regression comparison

Save the prior calculator output. For a re-audit, compare:

- final score;
- raw score;
- coverage;
- confidence;
- category scores;
- criterion ratings;
- gate status.

A changed rating requires new current evidence.
