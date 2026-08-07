# Changelog

## 1.2.0 — 2026-08-07

- Added mandatory `design-language.md` for reconstruction and migration modes.
- Separated evidence-backed reference observations, reusable principles, and target-product adaptations.
- Added explicit local reconstruction and production adaptation contracts.
- Added `Must replace` production blockers to prevent competitor identity from shipping unchanged.
- Required QA recalibration and links from planning, component specifications, QA, and handoff.

## 1.1.0 — 2026-08-07

- Clarified that the skill is page-scoped and does not automatically crawl or clone a whole site.
- Added reconstruction, adaptation, reconstruction-and-adaptation, owned-migration, and audit-only modes.
- Allowed development-only target media for high-fidelity reconstruction under strict isolation.
- Added `.reference-assets/` raw archives and `public/__reference__/` temporary served assets.
- Added centralized logical asset mapping to avoid scattered temporary paths.
- Added machine-readable asset manifest and replacement checklist templates.
- Added visual replacement constraints for dimensions, crop, focal point, transparency, layering, and motion.
- Added separate reconstruction QA and production QA milestones.
- Added `PROTOTYPE_ONLY` and `PRODUCTION_READY` release states.
- Added a non-destructive production gate script that blocks target assets, temporary manifest states, target domains, and brand-term remnants.
- Removed the requirement to force arbitrary structural differences during adaptation.

## 1.0.0 — 2026-08-07

- Reworked website cloning into an existing-project-first reference builder.
- Added reference, owned-migration, and audit-only modes.
- Added originality, brand, copy, asset, and font controls.
- Added repository integration safeguards for i18n, auth, credits, payments, analytics, SEO, and deployment.
- Added reference matrix, original design brief, implementation plan, component specification, asset provenance, and QA templates.
- Made browser tooling and worktrees optional capabilities rather than framework assumptions.
- Added Codex installation, discoverability snippet, validation script, and review prompt.
