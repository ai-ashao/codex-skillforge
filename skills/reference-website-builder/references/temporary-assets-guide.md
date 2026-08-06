# Temporary reference asset guide

Use this guide when original page media is needed to achieve high reconstruction fidelity before replacement.

## Purpose

Temporary target assets are development scaffolding. They help preserve:

- exact aspect ratios and crop behavior
- layered compositions
- transparency and masks
- foreground/background balance
- animation timing and video dimensions
- realistic text wrapping around media

They are not automatically approved for public release.

## Required directory roles

```text
.reference-assets/<slug>/raw/
public/__reference__/<slug>/
src/config/reference-assets.*
docs/reference-build/<slug>/asset-manifest.json
docs/reference-build/<slug>/replacement-checklist.md
```

Framework-specific paths may differ, but the roles must remain distinct.

### Raw archive

`.reference-assets/<slug>/raw/` contains original downloads and capture artifacts.

- never import it from application code
- normally add `.reference-assets/` to `.gitignore`
- do not execute any downloaded script
- preserve original filenames only when useful; prefer stable logical IDs in the manifest

### Temporary served directory

`public/__reference__/<slug>/` contains only files needed to render the local reconstruction.

- treat every file as development-only
- never mix it into normal production media directories
- remove it or empty it before production release
- avoid external hotlinks

### Central asset map

Create one logical asset registry, such as `src/config/reference-assets.ts`.

Components should request logical assets:

```ts
referenceAssets.hero.background.src
referenceAssets.workbench.preview.src
```

They should not repeat physical paths such as `/__reference__/...` throughout the component tree.

## Manifest fields

Every temporary asset should include:

- stable `id`
- `type`
- `sourcePage`
- `sourceUrl`
- `sourceHost`
- `temporaryPath`
- logical `usage`
- visual replacement constraints
- `status`
- `replacementPath`
- `productionApproved`
- license or authorization when known
- notes

## Replacement constraints

Record the visual role, not only the filename:

- width and height
- aspect ratio
- transparent or opaque background
- crop and focal point
- dominant luminance and contrast
- border radius or mask
- z-index and layering role
- autoplay, loop, poster, and duration for video
- whether mobile uses another crop or asset

A replacement is not ready merely because a new file exists. It must preserve the composition or intentionally update the design.

## Replacement workflow

1. Register the target asset as `temporary`.
2. Reconstruct and visually validate the page.
3. Produce or acquire a replacement.
4. Add its path to the manifest and asset map.
5. Mark it `replacement-ready`.
6. Re-run visual and interaction QA.
7. Record license/ownership.
8. Mark it `approved`.
9. Remove the temporary served file when no longer referenced.
10. Run the production release gate.

## Do not download

- JavaScript bundles for execution or source reuse
- private or authenticated user media
- secrets, tokens, API responses containing personal data
- proprietary font binaries without authorization
- media obtained by bypassing controls

## Git policy

Recommended `.gitignore` entry:

```gitignore
.reference-assets/
```

The machine-readable manifest and replacement checklist should normally be versioned. Whether temporary files under `public/__reference__/` are versioned depends on the team's prototype workflow, but they must never survive the production gate.
