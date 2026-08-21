---
name: adapt-reference-site
description: Reconstruct a mature reference product's validated information architecture, layout rhythm, interaction patterns, responsive behavior, and content density inside an existing target repository while following the user's explicit choice of reference design language, target-project design language, or staged reference-first styling. Use for competitor-pattern migrations, static-demo-to-production conversions, screenshot-led rebuilds, tool-site cloning requests, target-native pattern adoption, explicit competitor-design-language requests, staged migrations, multi-reference reconstruction, and later SEO expansion without drifting into freeform redesign or copying protected brand assets.
---

# Adapt Reference Site

Reconstruct validated product decisions, not source identity.

Default sequence:

**Evidence → Visual Policy → Pattern Spec → Structural Parity → Product Truth → SEO Expansion**

Do not begin with freeform redesign. Do not claim functionality that the evidence does not contain.

## Non-negotiable rules

- Preserve the target repository's framework, routing, styling approach, state boundaries, and completion commands unless the user explicitly changes them.
- Treat an existing approved target design system as authoritative unless the user explicitly requests the reference design language. Do not replace it merely to improve visual similarity.
- Reconstruct information architecture, geometry, density, responsive logic, and interaction pacing closely when they are in scope.
- Do not ship source logos, trademarks, proprietary illustrations, photographs, distinctive icons, unique animations, copied SEO text, or unlicensed assets.
- Isolate reference evidence from production assets and keep provenance visible.
- Preserve the target product's real functionality when it conflicts with the reference.
- Never invent a calculation engine, AI service, auth system, payment flow, stored data, or production deployment because a static Demo visually implies one.
- Keep deferred reference buttons visible when the user asks to preserve the Demo surface. Make them respond with an honest “In development” state instead of hiding or disabling them silently.
- Add technical SEO with the first public implementation. Delay content expansion until structural parity is stable.
- Preserve keyboard focus, narrow-screen usability, reduced-motion behavior, and semantic HTML.
- Keep existing reference files, screenshots, and unrelated dirty changes intact.

## Choose an execution mode

Select the mode from the user's wording and current project state. State the choice before editing.

Map explicit user language first:

- “Use the competitor/reference design language” → Reference-language migration
- “Use the project/our existing design language” → Target-native migration
- “Match the Demo first, replace the design language later” → Reference-first staged migration

If the user does not specify visual ownership:

1. preserve an approved target design system when one exists
2. otherwise infer from the project brief and reference evidence
3. if the choice would materially change the result, ask before styling

### Target-native migration

Use when the user requests the project's own design language, or by default when the target already has an approved design system and the user has not overridden it.

Migrate reference structure, interaction, density, and responsive decisions while implementing them with target-native components and tokens from the start. Do not first reproduce the reference skin and restyle it later.

### Reference-language migration

Use when the user explicitly requests the competitor's or reference's design language as the intended visual direction.

Reconstruct general visual roles closely, including palette relationships, type hierarchy, control geometry, border and shadow character, image treatment, and motion cadence. Still replace logos, trademarks, copied copy, proprietary imagery, distinctive icons, and other protected identity.

Treat this as an explicit visual-policy choice, not as permission for pixel-perfect cloning or asset reuse.

### Reference-first staged migration

Use only when the user explicitly says “first match the Demo,” “keep the reference look for now,” “replace the design language later,” or equivalent.

Execute structural reconstruction with a temporary, clearly documented reference-like skin. Replace source identity and protected assets immediately, but defer the target design-language pass.

Freeze the accepted structure before later visual redesign. Do not treat the temporary skin as final brand approval.

Do not select this mode merely because a reference screenshot or Demo exists.

### Audit only

Use when the user asks to review, compare, assess drift, or create a plan.

Inspect evidence and code, then report findings without editing production files.

## Resolve scope before implementation

Identify these inputs from the user, repository, and reference evidence:

### Reference

- exact URL, Demo directory, screenshots, or recording
- desktop, tablet, and mobile evidence
- section order and relative heights
- important interactions and states
- sticky, fixed, hidden, and reordered elements
- asset ownership or provenance status

### Target product

- product and brand name, including exact spelling
- launch language and route
- existing design tokens and reusable components
- real product functionality and missing functionality
- public routes and SEO infrastructure
- repository rules and verification command
- deferred integrations such as auth, AI, payment, persistence, and deployment

### Layer scope

Record whether each layer is preserved, replaced, deferred, or excluded:

1. information architecture
2. section order
3. grid and proportions
4. spacing rhythm
5. content density
6. CTA hierarchy
7. primary workflow
8. interaction behavior
9. responsive behavior
10. visual language
11. product functionality
12. technical SEO
13. content SEO

When unclear, preserve reference structure, target product behavior, and the target's existing visual language. Ask only when the missing choice materially changes the product.

## Separate four reference layers

### A. Structural pattern — highest fidelity

Reconstruct closely when in scope:

- information architecture and section order
- container widths and column ratios
- grid composition and major alignment
- relative section height and whitespace rhythm
- content grouping and density
- product-to-marketing balance
- CTA hierarchy
- placement of examples, pricing, FAQ, and internal-link blocks
- desktop-to-mobile rearrangement logic

Aim for structural parity, not source-code or pixel duplication.

### B. Interaction pattern

Reproduce useful logic and pacing:

- field order and progressive disclosure
- tabs, selectors, accordions, drawers, and menus
- primary action and result placement
- loading, empty, success, error, and deferred states
- sticky and fixed behavior
- mobile stacking and interaction cadence

If a reference control is not implemented yet, retain its visible role when requested and provide an accessible status message such as “Feature is in development.”

### C. Visual language

In target-native migration mode, use the target product's tokens, typography, radius, borders, shadows, buttons, forms, icons, imagery, and motion rules from the first implementation pass.

In reference-language migration mode, reconstruct the reference's general visual system while using target-owned assets and target-native copy. Document which visual roles come from the reference and which identity elements were replaced.

In reference-first staged mode, allow a temporary reference-like palette and rhythm only when the user explicitly wants visual parity first. Still replace identifying brand assets and document that target design language is deferred.

Never embed product-specific defaults for an unrelated brand in this generic Skill.

### D. Content layer

During reconstruction, match content role and approximate volume:

- headline role and length range
- subtitle density
- CTA count and label length
- card-copy volume
- FAQ count and answer depth
- section-copy volume

Write target-native copy. Do not reuse source slogans, claims, examples, legal text, or exact SEO phrasing.

## Workflow

### Phase 0 — Orient and protect the workspace

1. Read repository instructions and architecture completely.
2. Inspect package scripts, routes, styles, reusable components, tests, and Git status.
3. Identify existing dirty changes and reference-only directories.
4. Record the target verification command.
5. Determine whether the target already has an approved design language.
6. Confirm the chosen execution mode, visual-policy owner, and current non-goals.

Do not delete a reference Demo merely because production code no longer imports it.

### Phase 1 — Capture evidence

Inspect enough evidence to avoid coding from memory or a vague impression.

At minimum capture:

- full desktop page
- narrow mobile page
- one intermediate viewport when layout transforms materially
- interaction states for the primary workflow
- media inventory and asset provenance

If the Demo already contains screenshots, topology notes, behavior notes, and QA evidence, reuse them instead of repeating collection.

Do not download or execute source-site scripts merely to recover proprietary business logic.

### Phase 2 — Write a compact pattern spec

Create or update `REFERENCE_PATTERN.md` for substantial migrations. For a small implementation, keep the same information in the working plan.

Record:

- section sequence and purpose
- approximate relative height and density
- max-width, side padding, columns, gaps, and image-to-text ratios
- primary and secondary CTA hierarchy
- default, input, loading, result, error, and deferred states
- desktop, tablet, and mobile transformations
- content-volume ranges
- protected assets that require replacement
- deliberate deviations already approved by the user

Use measurements and ranges where helpful. Do not copy source CSS wholesale.

### Phase 3 — Reconstruct structure

Implement with target repository conventions and the visual policy selected in Phase 0.

Preserve unless accessibility, broken responsiveness, target functionality, or explicit user direction requires otherwise:

- section order
- layout ratios
- spacing rhythm
- content density
- major component placement
- interaction sequence
- CTA visibility and hierarchy
- responsive logic

Do not casually add, merge, remove, or reorder sections. Do not reduce FAQ density or simplify the closing CTA just to save implementation time. Document required deviations.

Prefer existing target components when they fit. Create a component only for repeated UI, a meaningful interaction boundary, a stable semantic section, or an established repository pattern.

### Phase 4 — Establish product truth

Create a capability matrix before claiming completion:

| Surface | Status | Required behavior |
|---|---|---|
| Existing real feature | connected | preserve and test |
| Static Demo interaction | preview | local state and honest notice |
| Deferred feature | in development | visible button and accessible feedback when requested |
| External integration | unconfigured | no production claim |
| Unknown business logic | blocked | do not invent results |

For a static-demo-to-product migration:

- implement real form semantics and local validation
- use correct input types
- preserve tabs and progressive fields
- disclose whether data is transmitted or stored
- keep unavailable actions honest
- separate UI completion from business-logic completion

Do not substitute a plausible formula for an unverified calculator. Put calculation rules in a pure, testable domain module only after authoritative examples exist.

### Phase 5 — Pass the structural parity gate

Do not start freeform styling or large content expansion until this gate passes.

#### Desktop

- section order matches the intended pattern
- major proportions and container widths are comparable
- whitespace rhythm and density are comparable
- the product surface has similar prominence
- CTA hierarchy is preserved
- the page silhouette is recognizably equivalent

#### Mobile

- stacking and order preserve reference intent
- the primary action remains prominent
- controls remain usable
- secondary content does not overwhelm the tool
- spacing does not inflate excessively
- no horizontal overflow exists

#### Product surface

- input hierarchy and form semantics are correct
- all visible controls respond
- empty, validation, deferred, and result states are explicit
- unavailable services are not presented as live
- keyboard operation and focus visibility work

If parity fails, fix structure before visual polish.

### Phase 6 — Verify visual-policy conformance

For target-native migration, confirm that structural roles map to existing target tokens:

```text
reference color role  -> target color token
reference type role   -> target type scale
reference radius      -> target radius token
reference control     -> target component
reference imagery     -> target-owned asset
reference motion      -> target motion rule
```

The mapping happens during reconstruction, not as a mandatory second styling pass.

For reference-language migration, verify visual-language parity in addition to structural parity:

- palette roles and contrast relationships
- typography hierarchy and density
- control height, radius, border, and shadow character
- imagery treatment and decorative intensity
- motion cadence and reduced-motion fallback

Do not use copied assets or exact brand identity as evidence of parity.

For reference-first staged migration, mark target-native styling deferred and preserve the accepted structure. Later visual work may change tokens and component styling but must not silently change layout, density, CTA hierarchy, or mobile order.

### Phase 7 — Add SEO in two layers

#### Technical SEO — implement with the first public route

- unique title and meta description
- canonical URL
- correct document language
- Open Graph and appropriate Twitter metadata
- robots and sitemap consideration
- one meaningful H1
- semantic headings and crawlable copy
- suitable structured data
- indexability appropriate to environment

Do not leave production defaults, starter-brand metadata, stale routes, or reference identity in public output.

#### Content SEO — expand after structural parity

May add or improve:

- explanatory copy
- FAQ depth
- examples and use cases
- internal links and related tools
- comparison or educational content
- query-specific sections below the primary product surface

Do not destabilize first-screen geometry, primary CTA hierarchy, or the core workflow. Put expansion below the stable product surface when possible.

### Phase 8 — Verify in proportion to risk

Run the repository's full completion command.

For web products also verify:

- formatting, lint, strict types, tests, and production build
- fresh-server HTTP behavior
- public metadata, canonical, robots, sitemap, and security headers
- desktop, laptop, tablet, and narrow-mobile screenshots
- interactive states and visible deferred-button feedback
- console errors
- image loading
- horizontal overflow
- keyboard focus and reduced-motion behavior

Static checks and a successful build do not replace browser verification.

When browser tooling modifies native controls during interaction, reload cleanly before classifying hydration warnings as application defects.

## Design freeze

After the user accepts desktop structure, mobile structure, navigation, primary workflow, CTA hierarchy, section rhythm, and density, mark them frozen.

Any later structural change must state:

1. what changed
2. why it changed
3. which reference principle is being overridden
4. whether mobile behavior changes

Copywriting, analytics, SEO expansion, payment integration, and design-token replacement must not silently rewrite the frozen structure.

## Multi-reference mode

Assign one responsibility to each reference before implementation. Do not average them together.

| Layer | Owner |
|---|---|
| Information architecture | Reference A |
| Primary interaction | Reference B |
| Responsive behavior | Reference A or B |
| Visual mood | Reference C or target product |
| SEO/content matrix | Reference D or research |
| Product rules and tokens | Target product |

The target product always owns final identity and functionality.

## Deliverables

### Lightweight execution

Use for a small tool page or a user request that says “implement it.”

- concise pattern spec in the plan or `REFERENCE_PATTERN.md`
- implementation code
- verification evidence
- short final report

### Full execution

Use for multi-page, multi-reference, redesign, or handoff work.

- `REFERENCE_PATTERN.md`
- `IMPLEMENTATION_PLAN.md`
- existing design-language source or `DESIGN.md`
- implementation code
- `VISUAL_QA.md`

Do not create auxiliary documents that do not help implementation or verification.

## Final report

Report:

- execution mode used
- structure, interactions, and responsive behavior preserved
- brand, assets, copy, routes, and functionality replaced
- visible deferred features and their behavior
- meaningful deviations and reasons
- desktop and mobile QA status
- technical SEO status
- content SEO status
- repository verification result
- production boundaries still deferred

## Default decisions

When uncertain about structure: preserve the reference.

When uncertain about visual language: preserve the target product's existing design system.

When uncertain about a branded element: replace it with a target-owned equivalent.

When uncertain about missing functionality: disclose the gap and do not invent behavior.

When uncertain about a deferred button: keep it visible with honest feedback if reference parity is the goal.

When uncertain about SEO placement: keep the product surface stable and expand below it.
