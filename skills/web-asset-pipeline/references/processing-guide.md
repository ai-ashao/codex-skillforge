# Processing Guide

## Directory and naming

Follow the target project’s established layout. If it has none, keep originals outside the production-served directory and put derivatives in a focused directory such as `public/images/`. Do not place source PSD, Figma exports, or multi-megabyte originals in the served output by default.

Use a role-based, lowercase hyphenated basename. Include the width only when multiple variants exist:

```text
passport-photo-editor-preview-640.webp
passport-photo-editor-preview-1280.webp
```

Do not use a filename as a replacement for meaningful alt text. Avoid names such as `final-v2`, source-provider identifiers, or invented product claims.

## Format decision

| Asset | Start with | Evaluate before shipping |
| --- | --- | --- |
| Simple logo/icon | SVG | Remove metadata and unsafe embedded content; keep a useful viewBox. |
| Screenshot/illustration | WebP | Compare target-size visual quality and byte size with source. |
| Photo/opaque background | AVIF and WebP | Choose the smallest acceptable result compatible with the project’s delivery path. |
| Transparent raster | WebP | Keep PNG only when quality, tooling, or compatibility needs it. |
| Animation | Native video, animated WebP, or CSS | Do not default to a large GIF. |
| CSS-only decoration | CSS/SVG | Do not introduce a bitmap unless it carries visual information CSS cannot. |

Format selection is a hypothesis until an encoded output has been measured. Never discard the source solely because an optimized candidate looks acceptable at one size.

## Responsive variants

Derive widths from the image’s maximum rendered CSS width and device-density needs. Avoid a fixed `640/1280/1920` set when it does not match the layout. Do not upscale a smaller source. For a full-width hero, a practical starting point is a mobile width and a desktop width; add a third only when the byte or crop difference is material.

Keep art-directed crops distinct from density variants. A mobile crop is a separate asset with its own review, not simply a resized desktop crop.

## Source and licence record

For external assets, record one line in the asset manifest before integration. Capture the exact source page, author/provider, acquisition date, licence terms or plan, attribution text/link, and the asset’s intended route. A provider home page is not enough evidence for an asset-specific licence.

AI-generated assets should record the generating service, prompt or generation identifier when available, generation date, and any material editing. This record helps trace later claims; it does not itself establish exclusivity or legal clearance.

Do not reuse competitor logos, product screenshots, photographed people, or recognisable trademarks merely because they were publicly reachable. Flag ambiguity to the user.

## Next.js and React integration

Use a local static import or a root-relative `src` for local images. For remote images, first confirm the project’s image configuration and remote-host policy. Avoid bypassing that policy with arbitrary URLs.

Set `width` and `height` or a stable `fill` container with an explicit aspect ratio. Supply `sizes` when the image uses responsive layout. Use `priority` only for the confirmed LCP image; default lazy loading is normally right for images below the fold. Make decorative images empty-alt and exclude them from information-bearing content.

For static React or HTML, use `srcset`/`sizes` or a `<picture>` element when delivering variants. Keep a width/height or CSS `aspect-ratio` reservation.

## Validation checklist

1. Compare source and derived bytes and dimensions.
2. Inspect crops at intended desktop and mobile widths, including transparent edges and dark/light backgrounds.
3. Confirm no layout shift and no broken asset request in browser developer tools.
4. Verify alt text, image priority, and responsive `sizes` match the page role.
5. Run the project checks; build success alone is not visual validation.
6. If the task targets performance, record the route, device/network profile, metric, and before/after values.
