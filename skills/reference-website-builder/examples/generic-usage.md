# 通用使用示例

## 单页面高保真重建并适配

```text
Use $reference-website-builder to reconstruct the user-supplied reference page inside the current repository:

REFERENCE_PAGE_URL

Scope: this URL only. Do not crawl the sitemap or automatically clone linked routes.
Mode: reconstruction-and-adaptation.

First reproduce the page's UI design language, topology, workbench layout, responsive behavior, hover states, scroll interactions, transitions, and layered media composition with high fidelity.

Create and maintain `docs/reference-build/<page-slug>/design-language.md`. Separate reference observations and evidence from reusable principles and new-site adaptations. Recalibrate it after reconstruction QA, then resolve its production adaptation contract and every `Must replace` item before release.

Development-only target assets may be downloaded when needed for fidelity, but they must be isolated under `.reference-assets/` and `public/__reference__/`, registered in `docs/reference-build/<page-slug>/asset-manifest.json`, and referenced through a centralized asset map. Record any temporary assets and their provenance in the handoff.

Preserve the repository's existing framework, i18n, authentication, credits, payments, analytics, consent, SEO routes, and Cloudflare deployment conventions. Do not scaffold a new app or upgrade the framework without a repository-driven reason.

After reconstruction QA, replace the target brand, logo, copy, favicon, OG image, testimonials, and temporary media with assets and content owned, generated, licensed, or authorized for the new site. Preserve each replacement's dimensions, crop, focal point, transparency, layering, and motion role.

Copy `scripts/check-reference-assets.mjs` into the target project and run it before the production build. Do not report production readiness until it passes.
```

## 仅高保真原型

```text
Use $reference-website-builder in reconstruction mode for REFERENCE_PAGE_URL.
Rebuild only that page in the current project and stop after visual and interaction QA.
Temporary target assets are allowed only through the isolation workflow.
Produce `design-language.md` even though production adaptation is out of scope, and record any temporary assets in the handoff.
```

## 只调研不改代码

```text
Use $reference-website-builder in audit-only mode for REFERENCE_PAGE_URL.
Analyze only this page. Produce topology, behaviors, design-language observations,
layered-media inventory, asset plan, and implementation plan without modifying code.
```

## 自有旧站迁移

```text
Use $reference-website-builder in owned-migration mode to migrate LEGACY_OWNED_PAGE_URL into the current repository. I own the source site and its content/assets. Record the authorization statement and provenance. Preserve the current repository's auth, billing, analytics, SEO, and deployment architecture. Do not attempt to recover private backend code or secrets.
```
