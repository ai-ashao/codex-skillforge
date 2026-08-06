export type ReferenceAssetStatus =
  | "temporary"
  | "replacement-ready"
  | "approved"
  | "removed";

export interface ReferenceAssetEntry {
  src: string;
  status: ReferenceAssetStatus;
  sourcePage?: string;
  sourceUrl?: string;
  productionApproved: boolean;
  replacementNotes?: string;
}

/**
 * Central asset map for a page reconstruction.
 *
 * Components should import logical entries from this file instead of embedding
 * /__reference__/ paths. Update this map when replacements are ready.
 */
export const referenceAssets = {
  hero: {
    background: {
      src: "/__reference__/replace-me/hero-background.webp",
      status: "temporary",
      sourcePage: "https://example.com/page",
      sourceUrl: "https://example.com/assets/hero.webp",
      productionApproved: false,
      replacementNotes: "Replace with owned/generated 16:9 background",
    } satisfies ReferenceAssetEntry,
  },
} as const;
