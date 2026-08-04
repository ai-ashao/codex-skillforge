---
name: web-asset-pipeline
description: Turn AI-generated images, stock assets, screenshots, Figma exports, logos, icons, product captures, and decorative visuals into production-ready web assets. Use when adding or replacing visual assets in a website; auditing oversized or untracked images; creating responsive WebP/AVIF variants; optimizing SVGs; selecting image formats; recording third-party asset rights; or integrating assets into Next.js, React, or static sites without harming visual quality, accessibility, or Core Web Vitals.
---

# Web Asset Pipeline

Create a traceable path from a visual source to a deployed web asset. Preserve the source, derive only the variants the rendered layout needs, and verify the resulting page in a browser.

## Operating rules

- Treat a competitor screenshot as visual reference, not a reusable asset. Recreate or license the visual before shipping it.
- Do not download, embed, or redistribute an external asset until its source URL, licence, attribution requirement, and permitted commercial use are known. Record uncertainty as a blocker, not as an assumed free licence.
- Keep source assets separate from production derivatives. Do not overwrite a user-provided original.
- Do not claim a size reduction, format conversion, or performance improvement until it has been measured on generated files or a rendered page.
- Do not rasterize a vector logo or icon merely for format uniformity. Do not convert a raster icon to SVG unless there is a legitimate vector source or a deliberate redraw.
- Do not promise that a flat screenshot can recover its original layers or transparent edges. Prefer an original export, recreate the element, or obtain a licensed replacement.

## Workflow

### 1. Establish the asset brief

For each requested visual, determine its page, role, rendered width and height, viewport relevance, source, and licence status. Use the existing project’s asset conventions when present; otherwise propose a small, explicit directory plan before moving files.

Classify the role as one of:

| Role | Default treatment |
| --- | --- |
| Logo or simple icon | Keep as an optimized SVG when a vector source exists. |
| UI screenshot or complex illustration | Use WebP by default; retain a source copy. |
| Photograph or large opaque background | Compare AVIF and WebP at the target display size. |
| Transparent illustration or object | Compare transparent WebP and PNG; keep PNG only when it is demonstrably necessary. |
| Decorative CSS shape or gradient | Prefer CSS or a small SVG over a bitmap. |
| Social preview | Produce the platform-required raster file, usually 1200 × 630, and verify metadata points to it. |

### 2. Audit before changing assets

Run the bundled audit from the project root. Pass only asset directories that exist:

```bash
python3 -B /path/to/web-asset-pipeline/scripts/audit_assets.py public assets src/assets
```

Use `--format json` for machine-readable output. The audit reports pathname, bytes, format family, dimensions when detectable, and a conservative review flag. It does not prove visual quality, licence status, or page usage.

Read `references/processing-guide.md` when choosing conversions, building an asset manifest, or integrating framework-specific images. Copy `assets/asset-manifest-template.csv` into the target project when the source and rights record does not already exist.

### 3. Create production derivatives

First crop to the intended composition, then resize to the largest actual rendered width. Generate additional widths only where the page needs materially different responsive renditions. Use semantic, stable, lowercase hyphenated names, such as `markdown-editor-preview-1280.webp`.

Use a project-supported image tool. If adding a converter dependency would change the project, ask before doing so; otherwise prefer an available local tool and record its output settings. Compare candidates at the target dimensions rather than applying fixed quality values.

For images that affect the first viewport, optimize the actual LCP candidate first. Avoid CSS-only background images for content that needs responsive sizing, meaningful alt text, or image optimization.

### 4. Integrate correctly

Update only the relevant page or component. Supply meaningful alt text for informative images; use an empty alt value only for genuinely decorative images. Reserve layout space with intrinsic dimensions or an equivalent stable aspect ratio.

For Next.js, use `next/image` for eligible local or configured remote images. Set `sizes` to the layout’s actual breakpoints. Set `priority` or `fetchPriority="high"` only for the one verified LCP image, not for every above-the-fold asset. Let lower-page images lazy load unless interaction requires otherwise.

### 5. Verify the delivered page

Perform proportionate checks:

1. Re-run the audit and compare measured bytes with the original.
2. Check every modified route at desktop and narrow mobile widths for crop, contrast, legibility, and layout shift.
3. Confirm the asset URL, intrinsic dimensions, alt text, and lazy/priority behavior in the rendered page.
4. Run the project’s relevant lint, typecheck, and build checks.
5. For performance work, collect a before/after measurement on the same route and test conditions. State any environmental limitations.

## Required handoff

Report:

- source and licence/attribution status for every new external asset;
- each original-to-derived mapping, including measured dimensions and bytes;
- all changed page or component references;
- actual validation performed and any remaining risks, such as unknown rights, unavailable responsive variants, or an image needing visual approval.

Never describe a build-only check as visual or production validation.
