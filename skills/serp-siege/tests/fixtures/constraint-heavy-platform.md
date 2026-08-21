# SERP Siege — constraint-heavy platform execution fixture

> Scenario fixture for workflow validation; not legal advice or a current market assessment.

## Execution Frame

- **Selected direction:** build a media utility around a third-party platform
- **Primary job:** help authorized users process their own media
- **Target scope:** metadata and user-supplied-file workflows
- **Destination:** `NOT_SUPPLIED`
- **Planning Confidence:** `LOW`

### Assumptions

| Assumption | Basis | Execution Impact | Confidence | Validation |
|---|---|---|---|---|
| only user-owned or authorized media is in scope | `MODEL_INFERENCE` | excludes protected-media extraction | `LOW` | obtain explicit user confirmation |

## Search Landscape Summary

- **Primary job:** process authorized media
- **Primary keyword cluster:** media metadata utility
- **SERP structure:** unavailable in fixture
- **Competitor pattern:** platform-dependent utilities
- **Execution-relevant coverage gaps:** authorized local workflows
- **Major unknowns:** permission model and API access
- **Research coverage:** fixture only

## Competitor Map

| Competitor | Positioning | Main Tool | Coverage | Strength | Weakness | Evidence |
|---|---|---|---|---|---|---|
| Example platform utility | media workflow | metadata inspection | partial | familiar task | platform dependency | `MODEL_INFERENCE`: fixture assumption |

## Keyword Cluster Map

| Cluster | Type | Primary Keyword | Intent | Supporting Queries | Page Decision | Priority | Evidence |
|---|---|---|---|---|---|---|---|
| media-metadata | `CORE` | media metadata viewer | inspect owned file | view media metadata | `NEW_TOOL_PAGE` | `P0` | `MODEL_INFERENCE`: fixture assumption |

## Feature Coverage Map

| Feature | Competitor A | Competitor B | Competitor C | Candidate | Priority | Evidence |
|---|---|---|---|---|---|---|
| Local metadata inspection | `PARTIAL` | `MISSING` | `MISSING` | `PLANNED` | `P0` | `MODEL_INFERENCE`: fixture assumption |

## SERP Coverage Map

| Cluster | Primary Keyword | Intent | Evidence | SERP Strength | Gap | Reuse Potential | Proposed Page | Priority |
|---|---|---|---|---|---|---|---|---|
| media-metadata | media metadata viewer | tool | `MISSING` | `MISSING` | `MISSING` | `HIGH` | /media-metadata-viewer | `P0` |

## SEO Page Map

| Page Decision | Proposed URL | Canonical Parent | Target Cluster | Primary Keyword | Search Intent | Shared Core | Priority | Reason |
|---|---|---|---|---|---|---|---|---|
| `NEW_TOOL_PAGE` | /media-metadata-viewer | | media-metadata | media metadata viewer | tool | local file parser | `P0` | lawful user-supplied-file workflow |
| `REJECT` | | | protected-media-extraction | protected media downloader | acquisition | none | `REJECT` | outside the authorized execution scope |

## First Batch

| Item or URL | Group | Target Cluster | Why Now | Shared Capability | SEO Role |
|---|---|---|---|---|---|
| /media-metadata-viewer | `CORE` | media-metadata | preserves a safe executable workflow | local file parser | focused tool entry |

The batch is narrowed to user-supplied files because platform authorization is not available.

## Product Roadmap

### MVP / P0

| Item | Shared Core | Required Workflow | Reason |
|---|---|---|---|
| metadata viewer | local file parser | choose file, inspect, export metadata | completes the authorized core job |

The first version does not retrieve or bypass protected platform media.

### P1

| Item | Demand Evidence | Core Reuse | Reason |
|---|---|---|---|
| `NONE` | | | no additional authorized workflow is evidenced |

### P2

| Item | Uncertainty or Cost | Revisit Evidence |
|---|---|---|
| official API import | platform authorization | documented API access |

## Do Not Build Yet

| Idea | Status | Reason to Hold or Reject | Revisit Trigger |
|---|---|---|---|
| protected-media extraction | `REJECT` | outside authorized scope | explicit lawful platform support |

## Execution Constraints & Missing Evidence

| Constraint or Unknown | Affected Scope | Recommended Adjustment | Evidence Type | Confidence | Prerequisite or Next Evidence |
|---|---|---|---|---|---|
| platform permission | remote import | use local user-supplied files only | `MISSING+MODEL_INFERENCE` | `LOW` | explicit platform authorization |

## Next Execution

- **First action:** define the local-file metadata contract.
- **Required evidence or prerequisite:** confirm authorized input boundaries.
- **Success condition:** the local workflow completes without protected access.
- **If it fails:** narrow supported formats.
- **First Batch re-evaluation trigger:** official API access becomes available.
