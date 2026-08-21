# SERP Siege Report Template

Use this template for every SERP Siege execution plan. The report must not contain project-admission decisions, opportunity scores, separation-risk scores, or architecture verdicts.

Use exactly these evidence labels:

- `FIRST_PARTY`
- `USER_SUPPLIED_THIRD_PARTY`
- `LIVE_PUBLIC_OBSERVATION`
- `MODEL_INFERENCE`
- `MISSING`

Multiple labels may be joined with `+`. Never replace them with aliases such as `VERIFIED` or `PUBLIC_OBSERVATION`.

## Execution report

```markdown
# SERP Siege — [candidate]

## Execution Frame

- **Selected direction:** [what the user has decided to pursue]
- **Primary job:**
- **Target scope:**
- **Destination:** [user-supplied destination or `NOT_SUPPLIED`]
- **Planning Confidence:** `HIGH` / `MEDIUM` / `LOW`

### Assumptions

| Assumption | Basis | Execution Impact | Confidence | Validation |
|---|---|---|---|---|
| | `FIRST_PARTY` / `USER_SUPPLIED_THIRD_PARTY` / `LIVE_PUBLIC_OBSERVATION` / `MODEL_INFERENCE` / `MISSING` | | `HIGH` / `MEDIUM` / `LOW` | |

Planning Confidence describes how complete the execution inputs are. It is not a judgment about whether the project is worth doing.

## Search Landscape Summary

- **Primary job:**
- **Primary keyword cluster:**
- **SERP structure:**
- **Competitor pattern:**
- **Execution-relevant coverage gaps:**
- **Major unknowns:**
- **Research coverage:**

## Competitor Map

| Competitor | Positioning | Main Tool | Coverage | Strength | Weakness | Evidence |
|---|---|---|---|---|---|---|
| | | | | | | `LIVE_PUBLIC_OBSERVATION`: source |

## Keyword Cluster Map

| Cluster | Type | Primary Keyword | Intent | Supporting Queries | Page Decision | Priority | Evidence |
|---|---|---|---|---|---|---|---|
| | `CORE` | | | | `NEW_TOOL_PAGE` | `P0` | |

## Feature Coverage Map

| Feature | Competitor A | Competitor B | Competitor C | Candidate | Priority | Evidence |
|---|---|---|---|---|---|---|
| | | | | | | |

## SERP Coverage Map

| Cluster | Primary Keyword | Intent | Evidence | SERP Strength | Gap | Reuse Potential | Proposed Page | Priority |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

## SEO Page Map

| Page Decision | Proposed URL | Canonical Parent | Target Cluster | Primary Keyword | Search Intent | Shared Core | Priority | Reason |
|---|---|---|---|---|---|---|---|---|
| `NEW_TOOL_PAGE` | /example | | cluster-name | | | | `P0` | |
| `SAME_PAGE` | | /example | synonym-cluster | | | | `HOLD` | merge into parent |
| `REJECT` | | | thin-permutation | | | | `REJECT` | duplicate intent |

## First Batch

| Item or URL | Group | Target Cluster | Why Now | Shared Capability | SEO Role |
|---|---|---|---|---|---|
| /example | `CORE` | cluster-name | | | |

[Explain deviations from the default 8–15 effective entrances.]

## Product Roadmap

### MVP / P0

| Item | Shared Core | Required Workflow | Reason |
|---|---|---|---|
| | | | |

State what the first version explicitly does not need.

### P1

| Item | Demand Evidence | Core Reuse | Reason |
|---|---|---|---|
| `NONE` or item | | | |

### P2

| Item | Uncertainty or Cost | Revisit Evidence |
|---|---|---|
| `NONE` or item | | |

## Do Not Build Yet

| Idea | Status | Reason to Hold or Reject | Revisit Trigger |
|---|---|---|---|
| | `HOLD` / `REJECT` | | |

## Execution Constraints & Missing Evidence

| Constraint or Unknown | Affected Scope | Recommended Adjustment | Evidence Type | Confidence | Prerequisite or Next Evidence |
|---|---|---|---|---|---|
| | | | `MISSING` | `LOW` | |

## Next Execution

- **First action:**
- **Required evidence or prerequisite:**
- **Success condition:**
- **If it fails:** [narrow, reorder, or adjust implementation]
- **First Batch re-evaluation trigger:**
```

The report may reject or defer individual pages and features, but it must not output `GO`, `CONDITIONAL_GO`, `NO_GO`, opportunity scores, separation-risk scores, or a verdict on whether the whole project should proceed.
