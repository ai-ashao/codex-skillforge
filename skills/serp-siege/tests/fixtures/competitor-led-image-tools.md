# SERP Siege — competitor-led browser-local image tools fixture

> Scenario fixture for workflow validation; not a current market assessment.

## Execution Frame

- **Selected direction:** build a browser-local image-tool product
- **Primary job:** prepare images for constrained uploads
- **Target scope:** compression-first image utilities
- **Destination:** `NOT_SUPPLIED`
- **Planning Confidence:** `MEDIUM`

### Assumptions

| Assumption | Basis | Execution Impact | Confidence | Validation |
|---|---|---|---|---|
| browser-local processing is required | `MODEL_INFERENCE` | defines the shared core | `LOW` | confirm with user |

## Search Landscape Summary

- **Primary job:** prepare images for constrained uploads
- **Primary keyword cluster:** image compression and resizing
- **SERP structure:** dedicated tools and broad suites
- **Competitor pattern:** single-purpose tools plus suites
- **Execution-relevant coverage gaps:** workflow fragmentation
- **Major unknowns:** current query metrics
- **Research coverage:** fixture only

## Competitor Map

| Competitor | Positioning | Main Tool | Coverage | Strength | Weakness | Evidence |
|---|---|---|---|---|---|---|
| Example suite | broad image utility | compression | broad | familiarity | fragmented workflow | `MODEL_INFERENCE`: fixture assumption |

## Keyword Cluster Map

| Cluster | Type | Primary Keyword | Intent | Supporting Queries | Page Decision | Priority | Evidence |
|---|---|---|---|---|---|---|---|
| image-compression | `CORE` | image compressor | compress an upload | compress jpg | `NEW_TOOL_PAGE` | `P0` | `MODEL_INFERENCE`: fixture assumption |

## Feature Coverage Map

| Feature | Competitor A | Competitor B | Competitor C | Candidate | Priority | Evidence |
|---|---|---|---|---|---|---|
| Compress | `YES` | `YES` | `MISSING` | `PLANNED` | `P0` | `MODEL_INFERENCE`: fixture assumption |

## SERP Coverage Map

| Cluster | Primary Keyword | Intent | Evidence | SERP Strength | Gap | Reuse Potential | Proposed Page | Priority |
|---|---|---|---|---|---|---|---|---|
| image-compression | image compressor | tool | `MODEL_INFERENCE`: fixture assumption | `MEDIUM` | `MEDIUM` | `HIGH` | /image-compressor | `P0` |

## SEO Page Map

| Page Decision | Proposed URL | Canonical Parent | Target Cluster | Primary Keyword | Search Intent | Shared Core | Priority | Reason |
|---|---|---|---|---|---|---|---|---|
| `NEW_TOOL_PAGE` | /image-compressor | | image-compression | image compressor | tool | client-side image pipeline | `P0` | establishes the core workflow |

## First Batch

| Item or URL | Group | Target Cluster | Why Now | Shared Capability | SEO Role |
|---|---|---|---|---|---|
| /image-compressor | `CORE` | image-compression | validates the main task | client-side image pipeline | core tool entry |

The fixture is intentionally smaller than the default batch because it tests structure, not market scope.

## Product Roadmap

### MVP / P0

| Item | Shared Core | Required Workflow | Reason |
|---|---|---|---|
| compression workflow | client-side image pipeline | upload, preview, compress, download | completes the primary job |

The fixture does not require accounts or cloud storage.

### P1

| Item | Demand Evidence | Core Reuse | Reason |
|---|---|---|---|
| resize workflow | `MODEL_INFERENCE` | high | adjacent task |

### P2

| Item | Uncertainty or Cost | Revisit Evidence |
|---|---|---|
| batch processing | browser performance | completion data |

## Do Not Build Yet

| Idea | Status | Reason to Hold or Reject | Revisit Trigger |
|---|---|---|---|
| cloud library | `HOLD` | violates low-maintenance preference | repeated save demand |

## Execution Constraints & Missing Evidence

| Constraint or Unknown | Affected Scope | Recommended Adjustment | Evidence Type | Confidence | Prerequisite or Next Evidence |
|---|---|---|---|---|---|
| current demand | supporting entrances | keep batch narrow | `MISSING+MODEL_INFERENCE` | `LOW` | refresh live SERP and supplied metrics |

## Next Execution

- **First action:** confirm the client-side image pipeline.
- **Required evidence or prerequisite:** refresh the live SERP.
- **Success condition:** the shared workflow supports the core tool and adjacent entries.
- **If it fails:** narrow the batch to compression only.
- **First Batch re-evaluation trigger:** new query or completion evidence.
