# SERP Siege — existing Markdown suite expansion acceptance fixture

> Scenario fixture for workflow validation; not a current market assessment.

## Execution Frame

- **Selected direction:** add a Markdown word-counter workflow to the existing suite
- **Primary job:** inspect Markdown document length
- **Target scope:** one focused tool page and shared parser extensions
- **Destination:** `EXISTING_SITE_PAGE`
- **Planning Confidence:** `LOW`

### Assumptions

| Assumption | Basis | Execution Impact | Confidence | Validation |
|---|---|---|---|---|
| existing page destination is user-selected | `FIRST_PARTY` | keep URLs on the host | `HIGH` | none |

## Search Landscape Summary

- **Primary job:** inspect Markdown document length
- **Primary keyword cluster:** Markdown word count
- **SERP structure:** missing live observation
- **Competitor pattern:** related writing utilities
- **Execution-relevant coverage gaps:** unknown
- **Major unknowns:** query breadth and completions
- **Research coverage:** fixture only

## Competitor Map

| Competitor | Positioning | Main Tool | Coverage | Strength | Weakness | Evidence |
|---|---|---|---|---|---|---|
| Existing host | Markdown utilities | format conversion | adjacent | existing audience | no validation yet | `MODEL_INFERENCE`: fixture assumption |

## Keyword Cluster Map

| Cluster | Type | Primary Keyword | Intent | Supporting Queries | Page Decision | Priority | Evidence |
|---|---|---|---|---|---|---|---|
| markdown-word-count | `ADJACENT_TOOL` | markdown word counter | inspect document | count Markdown words | `NEW_TOOL_PAGE` | `P0` | `MODEL_INFERENCE`: fixture assumption |

## Feature Coverage Map

| Feature | Competitor A | Competitor B | Competitor C | Candidate | Priority | Evidence |
|---|---|---|---|---|---|---|
| Word count | `MISSING` | `MISSING` | `MISSING` | `PLANNED` | `P0` | `MODEL_INFERENCE`: fixture assumption |

## SERP Coverage Map

| Cluster | Primary Keyword | Intent | Evidence | SERP Strength | Gap | Reuse Potential | Proposed Page | Priority |
|---|---|---|---|---|---|---|---|---|
| markdown-word-count | markdown word counter | tool | `MISSING` | `MISSING` | `MISSING` | `HIGH` | /markdown-word-counter | `P0` |

## SEO Page Map

| Page Decision | Proposed URL | Canonical Parent | Target Cluster | Primary Keyword | Search Intent | Shared Core | Priority | Reason |
|---|---|---|---|---|---|---|---|---|
| `NEW_TOOL_PAGE` | /markdown-word-counter | | markdown-word-count | markdown word counter | tool | Markdown parser | `P0` | smallest execution surface |

## First Batch

| Item or URL | Group | Target Cluster | Why Now | Shared Capability | SEO Role |
|---|---|---|---|---|---|
| /markdown-word-counter | `CORE` | markdown-word-count | tests demand on the host | Markdown parser | focused entry page |

The single-page batch is smaller than the default because this is an existing-site validation.

## Product Roadmap

### MVP / P0

| Item | Shared Core | Required Workflow | Reason |
|---|---|---|---|
| word counter page | Markdown parser | paste, count, inspect | minimum validation surface |

The first version does not need accounts or saved documents.

### P1

| Item | Demand Evidence | Core Reuse | Reason |
|---|---|---|---|
| reading-time breakdown | future GSC queries | high | expand only after demand appears |

### P2

| Item | Uncertainty or Cost | Revisit Evidence |
|---|---|---|
| document history | storage and privacy | repeated retention demand |

## Do Not Build Yet

| Idea | Status | Reason to Hold or Reject | Revisit Trigger |
|---|---|---|---|
| independent domain | `REJECT` | high intent and workflow overlap | strong independent query and brand evidence |

## Execution Constraints & Missing Evidence

| Constraint or Unknown | Affected Scope | Recommended Adjustment | Evidence Type | Confidence | Prerequisite or Next Evidence |
|---|---|---|---|---|---|
| query breadth | P1 expansion | ship one page first | `MISSING` | `LOW` | live SERP and host query data |

## Next Execution

- **First action:** define the shared Markdown parser interface.
- **Required evidence or prerequisite:** confirm the host route and navigation placement.
- **Success condition:** the page completes paste, count, and inspection workflows.
- **If it fails:** keep the feature embedded in the closest existing tool.
- **First Batch re-evaluation trigger:** query breadth supports additional entrances.
