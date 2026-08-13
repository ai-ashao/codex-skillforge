# Rights, branding, and asset provenance

This file is operational guidance, not legal advice.

## Development versus production

The workflow distinguishes two states:

### Development reconstruction

Target-page media may be downloaded and rendered temporarily when needed to reproduce composition, animation, and responsive behavior accurately.

Required conditions:

- exact page scope
- isolated temporary directories
- manifest registration
- centralized asset mapping
- provenance and replacement status recorded

### Production release

Every shipped asset must be:

- owned by the user
- generated for the project
- permissively or commercially licensed
- purchased for the project
- explicitly authorized as part of an owned migration

Otherwise it must be removed or replaced.

## Default release blockers

Unless explicitly authorized, these block production release:

- target logo, wordmark, product name, favicon, app icon, or OG image
- target marketing copy, testimonials, case studies, pricing claims, and legal text
- target product screenshots, bespoke illustrations, photography, animation, video, audio, or 3D assets
- customer data or identifiable user content
- proprietary font files
- target-host hotlinks
- code copied from minified bundles or developer tools
- hidden API endpoints, tokens, keys, private schemas, or user data

## Usually reusable as an implementation pattern

- common layout structures
- responsive behavior
- standard controls and interaction conventions
- spacing and hierarchy relationships
- card, tab, accordion, modal, sidebar, carousel, upload, and workbench patterns
- motion timing and state-transition concepts

Avoid deceptive impersonation or confusing brand identity.

## Production asset decision tree

1. Is it created by the user or already present with known rights? Approve and record it.
2. Was it generated specifically for this project? Record generation source and approval.
3. Is it licensed or purchased? Record URL, terms, attribution, and restrictions.
4. Is it from an explicitly authorized owned migration? Record authorization and original path.
5. Otherwise, keep it temporary and block release until replaced.

## Fonts

Identify the visual and metric characteristics, then:

- reuse an existing project font when suitable
- use a properly licensed official web font
- choose a metrically compatible alternative
- do not download proprietary target font binaries without authorization

## Copy

Target text may be recorded during reconstruction to reproduce geometry and state lengths. Before production release:

- replace brand and product names
- rewrite marketing copy for the user's product
- independently verify factual claims
- replace testimonials and legal text
- update translated content and metadata

Superficial synonym replacement is not sufficient when the result still impersonates the target.

## Required provenance record

Every production asset entry should include:

- logical asset ID
- final local path
- type
- creator/source
- source URL when applicable
- license or authorization
- attribution requirement
- allowed use
- status
- approval evidence or reviewer
