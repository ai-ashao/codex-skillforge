# Existing-project integration guide

## Repository discovery order

Read in this order when present:

1. root `AGENTS.md`, `CLAUDE.md`, `README.md`, contributing guides, and architecture docs
2. workspace/monorepo configuration
3. package manifests and lockfiles
4. route and app entry points
5. global styling and design tokens
6. shared components and page examples
7. i18n configuration and locale dictionaries
8. auth, payments, credits, API clients, analytics, consent, SEO, and deployment files
9. test and CI configuration

## Package manager

Infer from lockfiles and workspace configuration. Do not switch package managers.

- `pnpm-lock.yaml` → pnpm
- `yarn.lock` → yarn
- `package-lock.json` → npm
- `bun.lock` or `bun.lockb` → bun

Use existing scripts from the relevant package. In a monorepo, run commands from the correct workspace.

## Dependency policy

Before adding a dependency:

1. Search for an existing equivalent.
2. Check whether native platform or current UI primitives can handle it.
3. Verify compatibility with current framework and runtime.
4. Record why the dependency is needed.
5. Avoid framework upgrades or broad lockfile churn.

Do not copy package manifests from a reference implementation.

## Design-system policy

Prefer existing:

- tokens and CSS variables
- button, card, input, dialog, tab, accordion, tooltip, and navigation primitives
- icon packages
- breakpoints and containers
- animation utilities
- typography system

Introduce page-scoped tokens before changing shared global tokens. Shared-token changes require impact review across existing pages.

## Business-module protection

Treat these as high risk:

- authentication and session middleware
- billing, checkout, webhooks, and payment provider code
- credit or quota calculation
- database schema and migrations
- API signing and secret handling
- analytics identity and consent
- locale middleware and redirects
- sitemap, robots, canonical, and structured-data generation

Use their existing public interfaces. A visual redesign should not cause a rewrite of these modules.

## Git safety

- Check status before edits.
- Never reset, clean, checkout, or delete user changes without explicit instruction.
- If the working tree is dirty, isolate new files and avoid automated worktree orchestration.
- Create a baseline report of existing build/test failures.
- Keep changes small enough to review and revert.

## Empty or incompatible repositories

If no usable web application exists:

- do not silently scaffold a new project,
- document the missing foundation,
- provide a recommended stack only when asked,
- produce design and implementation artifacts that can be handed to a later project-creation step.
