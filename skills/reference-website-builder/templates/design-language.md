# Design Language

This artifact separates high-fidelity reference observation from the choices that may ship in the target product. Complete it during inspection, use it during implementation, recalibrate it after reconstruction QA, and update it again during adaptation.

## Document status

- Reference page URL:
- Target product and route:
- Mode: reconstruction / reconstruction-and-adaptation / owned-migration
- Last recalibrated after QA:

## Evidence rules

Label every reference claim as `Observed`, `Measured`, `Inferred`, or `Unknown`. Link measurements and screenshots where possible. Do not present an inferred token, implementation detail, or design intent as a fact.

## Local reconstruction contract

State what must be reproduced closely enough to compare the local page with the reference: visual hierarchy, geometry, responsive transitions, component states, interaction timing, and media composition. This contract governs the development prototype, not the production identity.

## Production adaptation contract

State how the target product will retain useful design principles while becoming recognizably its own product. Define required changes to brand identity, copy, metadata, assets, signature styling, and any potentially confusing trade dress. For an owned migration, document which identity elements are authorized to remain. Record unresolved items for the project owner to review.

## Typography

| Reference observation | Evidence status/source | Reusable principle | Target adaptation | Validation |
|---|---|---|---|---|

## Colors

| Reference observation | Evidence status/source | Reusable principle | Target adaptation | Validation |
|---|---|---|---|---|

## Layout and spacing

| Reference observation | Evidence status/source | Reusable principle | Target adaptation | Validation |
|---|---|---|---|---|

## Surfaces and depth

Include borders, radii, shadows, blur, gradients, overlays, and background treatments.

| Reference observation | Evidence status/source | Reusable principle | Target adaptation | Validation |
|---|---|---|---|---|

## Components

| Component/pattern | Reference observation | Reusable principle | Target adaptation | States to validate |
|---|---|---|---|---|

## Interactions and motion

| Trigger/state | Reference behavior and timing | Evidence status/source | Target adaptation | Reduced-motion behavior |
|---|---|---|---|---|

## Responsive behavior

| Range/transition | Reference behavior | Reusable principle | Target adaptation | Validation viewport |
|---|---|---|---|---|

## Accessibility

Document focus treatment, keyboard behavior, semantic structure, contrast, target sizes, announcements, and motion alternatives. Reference behavior never overrides accessibility requirements in the target project.

## Must preserve

List reusable principles or interaction qualities worth retaining. Describe principles, not competitor-owned identity elements.

## Must replace

List target brand names, logos, copy, metadata, favicons, OG images, testimonials, legal text, proprietary fonts, unapproved assets, distinctive illustrations, and other identity-bearing or confusingly similar elements. Each unresolved item is a production blocker unless explicitly authorized and documented.

| Item | Why it cannot ship as-is | Replacement owner/source | Status | Evidence |
|---|---|---|---|---|

## Adaptation decisions

Record deliberate differences introduced for the target product and why they improve brand fit, usability, accessibility, performance, or conversion.

## QA recalibration log

After visual and interaction QA, record which rules or tokens were corrected. Do not silently change the implementation without updating this artifact.

| Date | QA evidence | Previous rule | Calibrated rule | Affected implementation |
|---|---|---|---|---|

## Production release checklist

- [ ] The production adaptation contract is satisfied.
- [ ] Every `Must replace` item is replaced, removed, or explicitly authorized.
- [ ] Target-derived assets are `approved` or `removed` in the manifest.
- [ ] Brand, copy, metadata, and identity-bearing visuals are distinct for the target product or explicitly authorized for an owned migration.
- [ ] Accessibility requirements and reduced-motion behavior are verified.
- [ ] The production reference-asset gate passes.
