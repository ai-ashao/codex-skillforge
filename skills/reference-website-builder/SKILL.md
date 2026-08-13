---
name: reference-website-builder
description: Inspect an explicitly provided web page and reconstruct its UI design language, layout, responsive behavior, motion, interactions, and layered media inside an existing project. Use for page-level URL-to-code work, high-fidelity landing-page or workbench reconstruction, competitor-inspired UI adaptation, and authorized migrations. Produces a durable design-language contract that separates reference evidence from target adaptation. Development-only reference assets may be downloaded into isolated directories, but production release is blocked until branding, copy, metadata, and unapproved assets are replaced or authorized. Preserve the current stack, routes, i18n, auth, payments, analytics, SEO, and deployment conventions.
license: MIT
---

# Reference Website Builder

Reconstruct the page at an explicitly provided URL with high visual and interaction fidelity, then adapt it safely for the user's product. This is a **page-level workflow**, not an automatic whole-site crawler.

The default sequence is:

```text
inspect exact URL
→ high-fidelity page reconstruction
→ visual and interaction QA
→ brand/content/asset adaptation
→ optional release review
```

During reconstruction, target-site media may be used temporarily to preserve layered composition and visual accuracy. Temporary assets must remain isolated and traceable; the project owner decides whether and when to run a release review.

## Runtime requirements

Live-page inspection requires browser automation, and implementation requires a coding environment with filesystem access. The workflow is designed for Codex and other Agent Skills-compatible coding agents.

## Load supporting resources only when needed

- Read `references/inspection-guide.md` before inspecting a live page.
- Read `references/integration-guide.md` before changing an existing repository.
- Read `references/temporary-assets-guide.md` before downloading target-page media.
- Read `references/rights-and-provenance.md` before approving any asset for production.
- Read `references/qa-guide.md` before visual QA or release review.
- Use files in `templates/` for durable research, reconstruction, replacement, and QA artifacts.

## Inputs

Accept one or more explicit page URLs plus optional implementation instructions. Infer the current repository from the working directory.

Useful optional inputs:

- target project and route
- which URL supplies which page or section
- required fidelity level
- product brief, brand guide, screenshots, or PRD
- required languages and locale routes
- whether original target assets may be used temporarily
- whether the user owns or is authorized to migrate the source page
- scope: `audit-only`, `reconstruct`, `adapt`, or `reconstruct-and-adapt`

Do not require information that can be discovered from the repository or page. Record unresolved assumptions in the project context artifact.

### URL and rebranding instruction

Treat an instruction that supplies an explicit reference-page URL and names the desired final site as `reconstruct-and-adapt` for that exact URL:

```text
高保真重建以下页面：example.com
```

In that case, inspect and reconstruct only the user-supplied reference URL, while presenting the resulting site as `example.com`: replace the visible site name, logo treatment, favicon, metadata, and other brand identity. Preserve the reference page's layout and interaction language where appropriate, but do not retain the target's identity or imply an affiliation. Record any target-derived media or copy that remains as temporary. Do not embed third-party site names or URLs in the Skill's reusable instructions or examples; take them only from the current user request.

## Page scope

The scope is exactly the page or pages supplied by the user.

Default rules:

- Do not crawl the sitemap.
- Do not automatically follow navigation to clone other routes.
- Do not infer that the user wants the whole domain.
- Follow a link only when needed to observe an explicitly in-scope interaction, asset, or state.
- Additional pages require additional explicit URLs or user instruction.
- Keep research artifacts isolated by hostname and page slug when multiple URLs are provided.

## Operating modes

### 1. Reconstruction mode — default for implementation

Create a high-fidelity development implementation of the specified page.

In this mode:

- Preserve page topology, layout relationships, responsive behavior, motion, interactions, and layered-media composition when useful.
- Use measured computed styles and observed states rather than guessing.
- Target-site images, video, SVG, screenshots, or decorative media may be downloaded **temporarily** when needed for fidelity.
- Temporary assets must use the isolation workflow defined below.
- Record unapproved target assets, brand terms, original copy, favicons, OG images, and remote hotlinks in the manifest and handoff.

### 2. Adaptation mode

Convert a reconstructed page into the user's product page.

Adaptation includes:

- replacing brand identity, logo, favicon, OG image, and metadata
- replacing or authorizing temporary target assets
- replacing target copy with product-specific copy
- connecting existing product data and business modules
- adjusting SEO intent, locale content, and conversion path
- preserving the useful UI language, animation model, responsive behavior, and interaction quality

Structural changes are optional. Do not force arbitrary layout differences when the user's goal is to reuse a strong page pattern. Avoid deceptive impersonation or confusing brand identity.

### 3. Reconstruction-and-adaptation mode

Run reconstruction first, validate fidelity, then perform adaptation and any release review requested by the project owner.

### 4. Owned migration mode

Use only when the user explicitly states that they own the source page or have authorization to migrate it. Record that statement in `00-project-context.md`.

This mode may approve original content and assets for production, but still:

- record authorization and provenance
- do not extract secrets, private APIs, user data, authentication tokens, or backend source
- do not bypass access controls, paywalls, CAPTCHAs, or anti-bot protections
- rebuild only what browser-visible behavior and authorized source material support

### 5. Audit-only mode

Inspect and document the page and current repository without modifying production code.

## Non-negotiable principles

1. **Exact URL scope.** Reconstruct only explicit pages; never silently expand into whole-site cloning.
2. **Existing project first.** Preserve the repository's framework, package manager, routes, conventions, and working business modules.
3. **High fidelity before adaptation.** When reconstruction is requested, first reproduce observed layout, motion, interactions, and media composition accurately enough to judge the design.
4. **Temporary assets remain traceable.** Every target-site asset used during development must be isolated and registered with its provenance and replacement status.
5. **Centralized asset mapping.** Components must reference a project-level asset map, not scatter temporary paths throughout the codebase.
6. **Interaction model before component code.** Determine whether behavior is click-, hover-, keyboard-, scroll-, intersection-, time-, drag-, or state-driven.
7. **No guessing where inspection is possible.** Use screenshots, DOM inspection, computed styles, network-visible media URLs, and interaction sweeps.
8. **No source-code pretense.** Browser-visible inspection does not reveal the target's original source architecture or backend.
9. **Progressive integration.** Make small, reviewable changes and protect shared or business-critical files.
10. **Production release is a separate state.** A page may be visually complete but still blocked from release.

## Temporary asset isolation workflow

When target-page media is needed for reconstruction, use these roles:

```text
.reference-assets/<slug>/raw/       # research archive; never served
public/__reference__/<slug>/        # temporary dev-served assets
src/config/reference-assets.*       # centralized logical asset map

docs/reference-build/<slug>/
  design-language.md                 # observed rules, reusable principles, and target adaptation contract
  asset-manifest.json                # machine-readable source/status registry
  asset-provenance.md                # human-readable approval record
  replacement-checklist.md           # replacement progress and visual constraints
```

Adapt paths to the current framework when necessary, but preserve the semantic separation:

- raw research archive
- temporary served assets
- centralized logical map
- manifest and replacement record

### Required asset rules

- Never hotlink target media in production code.
- Do not place temporary target assets in normal production image folders.
- Do not reference `/__reference__/...` directly from many components. Route component usage through the asset map.
- Register every temporary asset in `asset-manifest.json`.
- Record its source URL, source page, type, purpose, temporary path, logical asset ID, replacement constraints, and production approval state.
- Add `.reference-assets/` to `.gitignore` unless the user explicitly wants the archive versioned and has the rights to do so.
- Do not download or redistribute proprietary font binaries without authorization. Use an approved or metrically compatible font.
- Logos, favicons, OG images, testimonials, legal text, and customer data remain release blockers unless authorized or replaced.

### Recommended asset states

- `temporary`: original target asset used only for development fidelity
- `replacement-ready`: replacement exists but has not passed visual QA
- `approved`: owned, generated, licensed, purchased, or authorized for production
- `removed`: no longer used

Only `approved` and `removed` are production-safe.

## Workflow

### Phase 0 — Resolve intent, page scope, and release target

1. Parse the explicit URLs and instructions.
2. Select a mode and scope.
3. Record whether the requested result is:
   - high-fidelity prototype only
   - adaptation candidate
   - production-ready deliverable
4. Create a slug and use:

```text
docs/reference-build/<slug>/
```

5. Copy `templates/project-context.md` to `00-project-context.md` and record:
   - user objective
   - exact page URLs
   - selected mode
   - target route
   - authorization status
   - temporary-asset policy
   - intended release status
   - repository constraints
   - assumptions and blockers

For reconstruction, reconstruction-and-adaptation, and owned-migration modes, also copy `templates/design-language.md`. Required output: `docs/reference-build/<slug>/design-language.md`. This is a durable artifact, not an optional summary.

In adaptation-only mode, read the existing `design-language.md` before editing. If it is missing, create it from the available reconstruction evidence, label gaps as `Unknown`, and do not invent reference observations.

If the request involves phishing, credential capture, deceptive impersonation, or fraudulent brand replication, stop and explain the issue.

### Phase 1 — Inspect the current repository

Read `references/integration-guide.md` and identify:

- package manager, framework, versions, workspace, and build commands
- route and rendering structure
- design tokens, shared components, icon and image pipeline
- i18n and locale routing
- authentication, credits, payments, API clients, analytics, and consent
- SEO metadata, sitemap, robots, canonical, hreflang, and structured data
- deployment target and runtime constraints
- repository instructions and current Git state
- existing asset configuration patterns

Write the baseline to `00-project-context.md`. Run the cheapest project-provided validation before edits.

Do not silently scaffold a new application or upgrade the stack.

### Phase 2 — Inspect the exact reference page

Read `references/inspection-guide.md`.

For each explicit URL:

1. Confirm accessibility without bypassing controls.
2. Capture full-page screenshots near 1440, 768, and 390 CSS pixels when practical.
3. Map page topology from top to bottom.
4. Perform scroll, click, hover, keyboard, autoplay/time, drag, and responsive sweeps as relevant.
5. Inspect computed styles for representative elements and unique variants.
6. Identify every layered image, background, overlay, mask, SVG, video, and poster that affects composition.
7. Record what is directly observed, measured, inferred, or unknown.
8. Do not automatically inspect unrelated routes.

Create:

```text
docs/reference-build/<slug>/
  01-reference-matrix.md
  02-page-topology.md
  03-behaviors.md
  references/
    <hostname>-desktop.png
    <hostname>-tablet.png
    <hostname>-mobile.png
```

Populate `design-language.md` from this evidence. For each design area, separate the reference observation from its evidence status, reusable principle, and target-product adaptation. The local reconstruction contract may require close visual fidelity; the production adaptation contract must define what changes before release.

### Phase 3 — Create reconstruction brief and asset plan

Copy `templates/original-design-brief.md` to `04-original-design-brief.md`.

For reconstruction mode, the brief must define:

- fidelity target and visual acceptance criteria
- page topology and component inventory
- typography, color, radius, elevation, iconography, and motion observations
- responsive behavior
- interaction models and states
- layered media composition
- which target assets are necessary temporarily
- asset replacement constraints such as dimensions, crop, transparency, focal point, motion, and contrast
- intended release state after this task

Treat `design-language.md` as the canonical cross-component record for typography, colors, layout and spacing, surfaces and depth, component patterns, interactions and motion, responsive behavior, accessibility, and production differentiation. The brief may summarize it but must not duplicate or replace it.

Create the asset artifacts before downloading target media:

```text
asset-manifest.json
asset-provenance.md
replacement-checklist.md
```

Use `templates/asset-manifest.json`, `templates/asset-provenance.md`, and `templates/replacement-checklist.md`.

### Phase 4 — Prepare isolated assets and centralized mapping

Read `references/temporary-assets-guide.md`.

1. Create the raw and served isolation directories.
2. Download only media required for the explicit page reconstruction.
3. Preserve source URLs and stable logical IDs in the manifest.
4. Copy or transform only the needed files into `public/__reference__/<slug>/` or the framework-equivalent dev-served location.
5. Create a centralized asset map using `templates/reference-assets.ts` or the project's native equivalent.
6. Point components to logical asset entries, not direct temporary paths.
7. Record the temporary-asset policy and any known release risks in project documentation.

Do not download scripts or execute code from the target site.

### Phase 5 — Plan repository integration

Copy `templates/implementation-plan.md` to `05-implementation-plan.md`.

The plan must include:

- files to create, modify, or leave untouched
- component boundaries
- route and locale changes
- existing modules to reuse
- asset map and manifest locations
- dependency additions with justification
- validation commands
- temporary-asset cleanup and release strategy
- risks to auth, credits, payments, analytics, SEO, and deployment
- how implementation tokens and components map to `design-language.md`

Classify files as:

- `safe-local`
- `shared-sensitive`
- `business-critical`

Make page-local changes first. Do not rewrite business-critical modules for visual convenience.

### Phase 6 — Write component specifications

For each non-trivial section, create:

```text
docs/reference-build/<slug>/components/<component>.spec.md
```

Each spec must include:

- product purpose
- reference observations and evidence
- DOM/component structure
- measured styles and project token mapping
- responsive behavior
- interaction model and all states
- content/data model
- logical asset IDs and temporary/approved state
- accessibility requirements
- integration points
- acceptance criteria

Link component-level decisions back to `design-language.md`. If a component needs an exception, record the reason in both places.

Split specifications that exceed roughly 150 lines for one implementation unit.

### Phase 7 — Reconstruct incrementally

1. Preserve the current framework, package manager, routing, and component conventions.
2. Build the shell and layout foundation first.
3. Implement bounded components incrementally.
4. Reuse existing primitives and dependencies where reasonable.
5. Reproduce observed motion and interaction models; document adaptations.
6. Use the centralized asset map for all target-derived temporary media.
7. Keep existing i18n, auth, credits, payments, analytics, consent, SEO, and API interfaces intact.
8. Run typecheck or equivalent after meaningful units.
9. Run the repository's full validation before reconstruction QA.

Parallel agents or Git worktrees are optional and allowed only when the runtime supports them, Git state is safe, and component boundaries are independent.

### Phase 8 — Reconstruction QA

Read `references/qa-guide.md` and create `06-qa-report.md`.

Compare the local implementation with the exact reference page at equivalent viewports and states. Validate:

- section order, geometry, containers, spacing, typography, radius, shadow, borders, and backgrounds
- layered media composition, crop, masks, transparency, and z-index
- hover, focus, active, tab, accordion, modal, carousel, sticky, scroll-driven, autoplay, drag, and responsive behavior
- mobile and tablet topology
- loading, empty, error, success, disabled, and long-content states where relevant
- build integrity and business-module regressions

At this stage, high visual similarity is expected. The QA report must list any temporary reference assets or target identity that remains.

Recalibrate `design-language.md` from QA evidence: correct inaccurate observations or tokens, record intentional deviations, and preserve the separation between the local reconstruction contract and production adaptation contract.

### Phase 9 — Adapt for the user's product

When adaptation is in scope:

1. Replace target brand identity, copy, metadata, favicon, OG image, testimonials, claims, and legal text.
2. Replace each temporary asset with an owned, generated, purchased, licensed, or explicitly authorized asset.
3. Preserve the replacement's visual role: dimensions, aspect ratio, focal point, transparency, contrast, layering, and animation timing.
4. Update the centralized asset map first; avoid editing component markup unless composition changes.
5. Change manifest entries from `temporary` to `replacement-ready`.
6. Repeat visual QA.
7. Promote an entry to `approved` only after visual and provenance review.
8. Connect real product data and existing business modules.
9. Update unique SEO and locale content.
10. Read and update `design-language.md`: implement the production adaptation contract, resolve every `Must replace` item, and record deliberate differences without discarding useful reusable principles.

The page may keep the reference's useful layout or interaction pattern. Do not force arbitrary structural divergence.

### Phase 10 — Optional release review

When the project owner requests a release review:

1. Copy `scripts/check-reference-assets.mjs` into the target repository or implement an equivalent project-native check.
2. Run it from the repository root.
3. Run the normal production build only after the check passes.
4. Confirm all of the following:
   - no served files remain under `public/__reference__/` or equivalent
   - no source code references `__reference__`
   - no manifest entry remains `temporary` or `replacement-ready`
   - no unapproved remote target-asset URL remains
   - no target logo, favicon, OG image, brand term, copied marketing copy, testimonial, legal text, or proprietary font remains unless authorized
   - metadata and locale content belong to the user's product
   - asset provenance is complete
   - the production adaptation contract in `design-language.md` is satisfied
   - every `Must replace` item is replaced, removed, or explicitly authorized

Recommended package-script pattern:

```json
{
  "scripts": {
    "check:reference-assets": "node scripts/check-reference-assets.mjs",
    "build:production": "npm run check:reference-assets && npm run build"
  }
}
```

If any issue remains, report it with its scope and recommended next action.

Never delete research evidence automatically. Remove or archive temporary served assets only after replacements pass QA.

### Phase 11 — Handoff

Final handoff must include:

- exact page URLs reconstructed
- implemented page and route
- fidelity and interaction QA results
- which assets remain temporary, replacement-ready, approved, or removed
- release-review result, if one was requested
- files changed
- validation commands and results
- unresolved issues and risks
- paths to research, manifest, replacement checklist, and QA artifacts
- path to `design-language.md`, its QA recalibration status, and unresolved `Must replace` items

## Failure handling

- **No browser automation:** Do not pretend inspection occurred. Produce a repository audit and an exact inspection checklist.
- **Target inaccessible:** Record the failure and use user-provided screenshots when available.
- **Build already failing:** Record baseline failures and separate them from introduced failures.
- **Dirty Git tree:** Do not reset or discard user changes; avoid automated worktree orchestration.
- **Asset download fails:** Use a visual placeholder, keep the logical asset ID, and record the missing source.
- **Unknown asset rights:** Continue only within the project's chosen temporary-asset policy and record the uncertainty.
- **Complex backend behavior:** Reuse existing interfaces or define a front-end state contract; do not infer private APIs.
- **Release requested with open issues:** List the exact issues and recommended next action.

## Completion standards

### Reconstruction complete

The exact page has been inspected and rebuilt with verified layout, responsive behavior, motion, interactions, and layered-media composition. `design-language.md` records evidence-backed observations, reusable principles, target adaptations, and QA recalibration. The project builds, and all temporary assets are isolated and registered. The result may remain prototype-only.

### Production adaptation complete

The requested adaptation is complete, the production adaptation contract and `Must replace` items are addressed as directed by the project owner, existing business systems still work, and the project passes the requested validation.
