#!/usr/bin/env node

/**
 * Non-destructive production release gate for page reconstruction projects.
 *
 * Usage:
 *   node scripts/check-reference-assets.mjs [project-root]
 *
 * Optional environment variables:
 *   REFERENCE_MANIFEST_GLOB is intentionally unsupported to keep this script
 *   dependency-free. Manifests are discovered under docs/reference-build/**.
 */

import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const projectRoot = path.resolve(process.argv[2] || process.cwd());
const failures = [];
const warnings = [];

const textExtensions = new Set([
  ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".vue", ".svelte",
  ".astro", ".html", ".css", ".scss", ".sass", ".less", ".json",
  ".md", ".mdx", ".yaml", ".yml", ".toml",
]);

const ignoredDirectoryNames = new Set([
  ".git", "node_modules", ".next", ".nuxt", ".output", "dist", "build",
  "coverage", ".turbo", ".vercel", ".wrangler", ".reference-assets",
]);

function relative(filePath) {
  return path.relative(projectRoot, filePath) || ".";
}

function walkFiles(startPath, options = {}) {
  const results = [];
  if (!fs.existsSync(startPath)) return results;

  const stack = [startPath];
  while (stack.length) {
    const current = stack.pop();
    let stat;
    try {
      stat = fs.lstatSync(current);
    } catch (error) {
      warnings.push(`Cannot inspect ${relative(current)}: ${error.message}`);
      continue;
    }

    if (stat.isSymbolicLink()) continue;
    if (stat.isFile()) {
      results.push(current);
      continue;
    }
    if (!stat.isDirectory()) continue;

    const name = path.basename(current);
    if (current !== startPath && ignoredDirectoryNames.has(name)) continue;

    let entries;
    try {
      entries = fs.readdirSync(current);
    } catch (error) {
      warnings.push(`Cannot read ${relative(current)}: ${error.message}`);
      continue;
    }

    for (const entry of entries) {
      stack.push(path.join(current, entry));
    }
  }
  return results;
}

function findManifestFiles() {
  const root = path.join(projectRoot, "docs", "reference-build");
  return walkFiles(root).filter((file) => path.basename(file) === "asset-manifest.json");
}

function readJson(file) {
  try {
    return JSON.parse(fs.readFileSync(file, "utf8"));
  } catch (error) {
    failures.push(`Invalid JSON in ${relative(file)}: ${error.message}`);
    return null;
  }
}

function nonEmptyFiles(directory) {
  return walkFiles(directory).filter((file) => fs.statSync(file).size >= 0);
}

const servedReferenceDirectories = [
  path.join(projectRoot, "public", "__reference__"),
  path.join(projectRoot, "static", "__reference__"),
  path.join(projectRoot, "src", "assets", "__reference__"),
];

for (const directory of servedReferenceDirectories) {
  const files = nonEmptyFiles(directory);
  if (files.length) {
    failures.push(
      `${relative(directory)} still contains ${files.length} development-only reference asset(s).`
    );
  }
}

const manifestFiles = findManifestFiles();
if (!manifestFiles.length) {
  warnings.push("No docs/reference-build/**/asset-manifest.json file was found.");
}

const targetHosts = new Set();
const brandTerms = new Set();

for (const manifestFile of manifestFiles) {
  const manifest = readJson(manifestFile);
  if (!manifest) continue;

  if (manifest.productionReady !== true) {
    failures.push(`${relative(manifestFile)} has productionReady=${String(manifest.productionReady)}.`);
  }

  for (const term of manifest.brandTerms || []) {
    if (typeof term === "string" && term.trim()) brandTerms.add(term.trim());
  }

  const assets = Array.isArray(manifest.assets) ? manifest.assets : [];
  for (const asset of assets) {
    const id = asset?.id || "<missing-id>";
    const status = asset?.status;
    if (!["approved", "removed"].includes(status)) {
      failures.push(`${relative(manifestFile)} asset ${id} has blocking status '${String(status)}'.`);
    }
    if (status === "approved" && asset?.productionApproved !== true) {
      failures.push(`${relative(manifestFile)} asset ${id} is approved but productionApproved is not true.`);
    }
    if (typeof asset?.sourceHost === "string" && asset.sourceHost.trim()) {
      targetHosts.add(asset.sourceHost.trim().toLowerCase());
    }
    if (typeof asset?.sourceUrl === "string") {
      try {
        targetHosts.add(new URL(asset.sourceUrl).hostname.toLowerCase());
      } catch {
        // A malformed URL is already visible in the manifest and can be reviewed manually.
      }
    }
  }
}

const scanRoots = [
  "src", "app", "pages", "components", "public", "static", "styles", "content",
].map((item) => path.join(projectRoot, item));

const candidateFiles = scanRoots
  .flatMap((scanRoot) => walkFiles(scanRoot))
  .filter((file) => textExtensions.has(path.extname(file).toLowerCase()));

for (const file of candidateFiles) {
  let content;
  try {
    content = fs.readFileSync(file, "utf8");
  } catch (error) {
    warnings.push(`Cannot read ${relative(file)}: ${error.message}`);
    continue;
  }

  if (content.includes("__reference__")) {
    failures.push(`${relative(file)} still references '__reference__'.`);
  }

  const lower = content.toLowerCase();
  for (const host of targetHosts) {
    if (host && lower.includes(host)) {
      failures.push(`${relative(file)} still contains target host '${host}'.`);
    }
  }

  for (const term of brandTerms) {
    if (term.length >= 3 && lower.includes(term.toLowerCase())) {
      failures.push(`${relative(file)} still contains target brand term '${term}'.`);
    }
  }
}

const uniqueFailures = [...new Set(failures)];
const uniqueWarnings = [...new Set(warnings)];

console.log(`Reference asset production gate: ${projectRoot}`);

if (uniqueWarnings.length) {
  console.log("Warnings:");
  for (const warning of uniqueWarnings) console.log(`  - ${warning}`);
}

if (uniqueFailures.length) {
  console.error("Production release blocked:");
  for (const failure of uniqueFailures) console.error(`  - ${failure}`);
  console.error(`\nPRODUCTION_READY=false (${uniqueFailures.length} blocker(s))`);
  process.exit(1);
}

console.log("Production reference-asset checks passed.");
console.log("PRODUCTION_READY=true");
