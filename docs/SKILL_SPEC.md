# SkillForge Skill Package Specification

This document defines the Phase A package contract for SkillForge v2. It separates the portable Agent Skill from optional repository engineering metadata.

## Portable package

Every Skill is an independently installable directory:

```text
skills/<skill-name>/
├── SKILL.md                 # required portable contract
├── agents/openai.yaml       # optional host UI metadata
├── references/              # optional on-demand guidance
├── scripts/                 # optional deterministic helpers
├── assets/                  # optional inputs or templates
├── tests/                   # optional Skill-owned tests
├── evals/                   # optional SkillForge eval specifications
└── skillforge.yaml          # optional SkillForge engineering metadata
```

Copying the Skill directory into `~/.codex/skills` must remain sufficient for Codex to use it. Installed Skills must not depend on the `skillforge` Python package at runtime.

## `SKILL.md`

`SKILL.md` must begin with YAML frontmatter and contain Markdown instructions after it.

Required frontmatter:

```yaml
---
name: example-skill
description: Explain what the Skill does and the requests that should trigger it.
---
```

Rules:

- `name` uses lowercase letters, digits, and single hyphens, is at most 64 characters, and exactly matches the directory name.
- `description` is a non-empty string of at most 1,024 characters. It should state both capability and triggering context.
- Portable compatibility fields currently accepted in addition to `name` and `description` are `license`, `allowed-tools`, and `metadata`.
- Markdown instructions must not be empty.
- A `SKILL.md` longer than 500 lines produces a warning because it exceeds the recommended context budget.

## Local references and paths

Inline Markdown links in `SKILL.md` are checked without fetching external URLs.

- Relative local links must resolve to an existing file or directory inside the Skill root.
- Absolute local paths and `..` traversal outside the Skill root are errors.
- URL, protocol-relative, query, and fragment-only destinations are not fetched.
- A symbolic link that resolves outside the Skill root is an error. An internal symbolic link is a portability warning.

Phase A checks inline Markdown links in every packaged Markdown file. Reference-style Markdown links and paths mentioned only in prose or code blocks are not interpreted as package dependencies.

## `agents/openai.yaml`

This file is optional. When present, it must be UTF-8 YAML with an `interface` mapping. `display_name`, `short_description`, and `default_prompt` must be strings when provided. A default prompt that does not mention `$<skill-name>` produces a warning rather than breaking legacy packages.

## `skillforge.yaml`

This optional file contains SkillForge engineering metadata and is not part of the portable execution contract. Version 1 accepts these top-level fields:

```yaml
schema_version: 1

skill:
  name: example-skill
  type: hybrid # deterministic, procedural, or hybrid

validation:
  commands:
    - id: unit
      argv: [python3, -B, -m, unittest, discover, -s, tests, -v]
      timeout_seconds: 120

evals:
  triggers: evals/triggers.json
  behavior: evals/behavior.json
  rubric: evals/rubric.json
```

Command entries use an argument vector instead of a shell string. Phase A validates but never executes them. Eval paths are relative to the Skill root, may not escape it, and must exist when configured. Unknown schema versions and unknown top-level fields fail clearly instead of being silently reinterpreted.

The initial v2 design draft illustrated `validation.commands` as shell strings. The v1 contract deliberately replaces that draft form with structured `argv` mappings so a later test runner does not require shell evaluation. String commands are rejected rather than silently split or executed.

The machine-readable contract is [`contracts/skillforge-config.v1.json`](../contracts/skillforge-config.v1.json).

## Static package validation

Install the single runtime dependency, then run validation from the repository root:

```bash
python3 -m pip install -r requirements.txt
python3 -m skillforge validate skills/technical-seo-audit
python3 -m skillforge validate --format json skills/technical-seo-audit
```

The validator does not execute Skill scripts, install dependencies, or access the network. It reports obvious remote-pipe, destructive-root, privileged, and dependency-install patterns found in `scripts/`. Pattern findings are evidence for review, not proof of intent.

Text and JSON output use these exit codes:

| Code | Meaning |
|---|---|
| `0` | Package has no error findings. Warnings may remain. |
| `1` | Package validation produced at least one error. |
| `2` | CLI invocation is invalid. |
| `3` | SkillForge encountered an internal error. |

JSON output follows [`contracts/skill-package.v1.json`](../contracts/skill-package.v1.json). Each finding has a stable `code`, `severity`, `path`, `message`, and optional `evidence` value.

## Legacy compatibility

`skillforge.yaml` is optional. Existing Skills can pass package validation without adding it, changing their scripts, or changing their installation method. Deterministic test execution, read-only readiness review, routing evals, and behavior evals are separate later layers; a Phase A package pass does not claim those assurances.
