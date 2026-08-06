# Live-page inspection guide

Use this guide only after exact page scope and repository context are recorded.

## Tool requirement

Use browser automation such as Chrome, Playwright, Puppeteer, or Browserbase. A normal HTTP fetch is not a substitute for interaction inspection. Do not bypass login, paywalls, CAPTCHAs, geo restrictions, or anti-bot controls.

## Scope discipline

- Open only the explicit URL by default.
- Do not crawl the sitemap or clone navigation destinations automatically.
- Follow another URL only to observe an in-scope interaction or asset, and record why.
- When multiple URLs are supplied, inspect each independently and isolate artifacts by hostname/page slug.

## Capture sequence

1. Open the exact URL.
2. Record final URL, redirects, locale, cookie/consent state, and viewport.
3. Capture full-page screenshots at desktop, tablet, and mobile widths when possible.
4. Map sections and fixed overlays.
5. Scroll slowly from top to bottom before clicking controls.
6. Click each meaningful tab, accordion, dropdown, carousel control, modal trigger, and safe CTA.
7. Hover buttons, links, cards, images, and navigation items.
8. Test keyboard tab order, focus styles, Escape behavior, and Enter/Space activation.
9. Resize between representative widths and identify actual layout changes.
10. Inspect computed styles for representative elements and unique component variants.
11. Inventory layered media and state-specific media.

## Interaction model

For every interactive area, state one or more drivers:

- click
- hover
- keyboard
- scroll position
- viewport intersection
- time/autoplay
- drag/swipe
- form/input state
- server/data state

Do not implement a click-based substitute for a scroll-driven interaction without documenting the adaptation.

## Computed-style sampling

Inspect properties that affect reconstruction:

- typography: family, size, weight, line height, letter spacing
- geometry: width, max width, height, padding, margin, gap
- layout: display, grid columns, flex direction, alignment, order
- visual: colors, borders, radius, shadow, filter, backdrop filter
- positioning: position, inset, z-index, overflow, sticky offset
- media: dimensions, object fit, aspect ratio, masking, clipping, layering
- motion: transition properties, duration, easing, transform, opacity, delay

Sample representative elements; do not dump the entire DOM without purpose.

## Layered media inventory

For each visually important section, inspect:

- `<img>`, `<picture>`, `<source>`, `<video>`, poster, and inline SVG
- CSS background images and masks
- absolutely positioned overlays
- multiple images in the same parent
- desktop/mobile asset swaps
- animated or autoplay media
- source dimensions and rendered dimensions

Assign each media item a stable logical ID before downloading it.

## Content handling

Visible text may be recorded during reconstruction to reproduce hierarchy, line length, and state geometry. Mark it as temporary reference copy. Before production release it must be replaced or authorized.

## Evidence quality

Distinguish:

- directly observed
- measured from computed style
- inferred from behavior
- inferred from DOM naming or public metadata
- unknown

Do not state an inference as confirmed source-code behavior.
