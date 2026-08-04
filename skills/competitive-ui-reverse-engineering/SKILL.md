---
name: competitive-ui-reverse-engineering
description: Analyze competitor websites, screenshots, landing-page references, and visual designs to extract reusable interface, conversion, and information-architecture patterns, then turn them into a differentiated implementation plan. Use when recreating a UI from screenshots, researching a successful landing page, planning a competitor-inspired SEO tool or SaaS page, improving an existing page from visual references, or producing a Next.js/React/Tailwind component plan and coding prompt. Do not use to copy a competitor’s copyrighted assets, branded content, or exact design.
---

# Competitive UI Reverse Engineering

Use visual references as research inputs, not as a source of production assets or a claim that a design caused commercial success. Extract the user task and interaction pattern, then make deliberate choices for the target product.

## Guardrails

- Do not copy a competitor’s logo, text, illustrations, screenshots, product data, trademark, or distinctive artwork. Treat screenshots as references only.
- Do not present a visual observation as a verified fact about traffic, conversion, rankings, revenue, or A/B-test performance. Mark it as an inference unless supported by current evidence.
- Do not use a screenshot to infer hidden behavior, accessibility, responsive states, implementation details, or licensing. Inspect the live page or source only when available, and label limits.
- Do not recommend a near-duplicate landing page. Tie every retained pattern to the target user’s task and state a meaningful product, workflow, content, or audience difference.
- Do not turn a visual analysis into a code change unless the user asks for implementation.

## Workflow

### 1. Frame the target and evidence

Record the target product, primary user task, audience, route, conversion goal, framework constraints, and available references. State which observations come from a live page, screenshot, supplied copy, or inference.

When a live URL is provided and browsing is available, inspect the current desktop and mobile page before relying on a screenshot. When only a screenshot is available, identify cropped, obscured, and unknown areas instead of filling them with invented detail.

### 2. Decompose the page

Map the page from top to bottom. Identify the navigation, hero, primary call to action, task input or product preview, trust signals, feature explanation, workflow, FAQ, secondary conversion paths, and footer.

For every important section, capture:

- user question or objection addressed;
- hierarchy, layout, and interaction pattern;
- visible copy role, not copied competitor wording;
- evidence status and confidence;
- whether the pattern is worth keeping, changing, or omitting.

Use the component boundary, not the pixel region, as the unit of analysis. A desktop screenshot rarely tells you where the responsive component boundary belongs.

### 3. Separate code from assets

Classify each visible element:

| Category | Default approach |
| --- | --- |
| Text, buttons, forms, cards, tables, tabs, navigation | Rebuild with semantic HTML and CSS/components. |
| Simple icon, line, gradient, or shape | Recreate with an existing icon set, CSS, or an original SVG. |
| Product UI | Rebuild a truthful state, a clearly labelled mock, or an actual product capture. |
| Photo, illustration, complex texture, 3D object | Create or obtain a separately licensed original asset. |
| Competitor brand/product material | Do not reuse; replace with target-product material. |

For asset specifications and production integration, invoke `$web-asset-pipeline`. Provide intended route, role, rendered dimensions, transparency, crop, source/right status, and LCP relevance.

### 4. Extract the underlying strategy

Explain why a pattern may help the user move forward. Consider:

- clarity of the first-screen promise and action;
- task flow and input friction;
- timing and specificity of trust signals;
- information hierarchy and progressive disclosure;
- comparison, FAQ, and objection handling;
- mobile constraints and accessibility implications.

Distinguish `OBSERVED`, `INFERRED`, and `UNKNOWN`. Do not call a pattern “proven” merely because a competitor uses it.

### 5. Design a differentiated target page

Produce a `KEEP / CHANGE / ADD / OMIT` decision for each material pattern. Prioritize changes that improve the target’s user task, content accuracy, trust, or workflow rather than superficial color changes.

For SEO-oriented pages, evaluate the page’s stated user intent, visible H1 role, task-first content, FAQ candidates, internal-link destinations, and sustainable content expansion. Do not invent search volume, keyword difficulty, or ranking potential. Use current keyword/SERP evidence if the task requires a demand claim.

### 6. Produce an implementation-ready plan

Propose semantic components, data/state boundaries, responsive behavior, accessibility requirements, and performance priorities. Default to the target project’s stack. If none is specified, propose a minimal Next.js + TypeScript + Tailwind structure without assuming shadcn/ui is installed.

Generate a coding prompt only after stating the product-specific differences and the assets that must be supplied. Require browser checks at desktop and narrow mobile widths; build success alone does not validate visual fidelity.

## Required output

Use `references/analysis-template.md` unless the user asks for a shorter result. Include:

1. target and evidence limits;
2. competitor/reference UI summary;
3. section and component map;
4. conversion and task-flow analysis;
5. SEO/content opportunities, clearly separating evidence and inference;
6. `KEEP / CHANGE / ADD / OMIT` decisions;
7. asset brief with rights status;
8. component and responsive architecture;
9. implementation prompt and validation plan, if requested.

## Completion standard

A complete result preserves the useful interaction pattern while making the resulting page clearly original, truthful to the target product, responsive, accessible, and feasible to implement. It must name material uncertainty and avoid copied copy or assets.
