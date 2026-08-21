# Page Mapping Rules

Assign exactly one treatment to every retained cluster. These are page-level execution decisions, not project-admission decisions.

## `SAME_PAGE`

Use when queries share the same intent, workflow, controls, output, and substantially similar SERP. Fold synonyms and shallow modifiers into the parent page.

## `NEW_LANDING_PAGE`

Use when a distinct audience, use case, constraint, or localized requirement needs different framing but can use the same underlying tool workflow. The page must add useful guidance or configuration, not only swap keywords.

## `NEW_TOOL_PAGE`

Use when the primary task, controls, input/output, or completion state materially differs. Name the shared core and the incremental build required.

## `CATEGORY_PAGE`

Use when several independently useful child tools form a coherent navigational and search theme. Do not create an empty hub for only one page.

## `CONTENT_SUPPORT`

Use for guides, specifications, comparisons, or troubleshooting intent that helps users complete the tool task. It must support a named cluster and internal-link destination.

## `REJECT`

Use for thin permutations, unsupported demand, brand-navigation dependence, policy risk, duplicate intent, or ideas outside the candidate's product core.

A rejected row may omit `Proposed URL`, but it must name the parent cluster and execution reason. Do not use `REJECT` to conclude that the user's whole project should be abandoned.

## Page decision test

Before proposing a URL, state:

1. named cluster;
2. dominant search intent;
3. distinct user value;
4. shared product capability;
5. incremental workflow or content;
6. cannibalization risk;
7. evidence and confidence.

If distinct user value or evidence cannot be stated, choose `SAME_PAGE` or `REJECT`. For `SAME_PAGE`, name the canonical parent URL.
