# Reference Asset Replacement Checklist

## Optional release review

- Requested: yes / no
- Review command:
- Last review result:

## Asset replacements

| Asset ID | Temporary path | Visual role | Replacement constraints | Replacement path | Status | Visual QA | Provenance approved | Owner/notes |
|---|---|---|---|---|---|---|---|---|

Statuses: temporary / replacement-ready / approved / removed.

## Identity and content cleanup

- [ ] Target logo and wordmark replaced or authorized
- [ ] Target product/brand name removed from visible UI
- [ ] Favicon and app icons replaced or authorized
- [ ] OG/social images replaced or authorized
- [ ] Metadata belongs to the user's product
- [ ] Marketing copy rewritten or authorized
- [ ] Testimonials and claims replaced or authorized
- [ ] Legal text replaced with project-specific text
- [ ] Proprietary fonts removed or authorized
- [ ] Target-host hotlinks removed

## Temporary directory cleanup

- [ ] No source code references `__reference__`
- [ ] `public/__reference__/` is empty or removed
- [ ] Raw archive is not served
- [ ] `.reference-assets/` is ignored or intentionally controlled
- [ ] Manifest contains only approved or removed entries

## Final verification

- [ ] Replacement visual QA passed at desktop, tablet, and mobile
- [ ] Interaction QA passed after replacement
- [ ] `node scripts/check-reference-assets.mjs` passed
- [ ] Normal production build passed after the gate
