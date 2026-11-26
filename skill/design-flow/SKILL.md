---
name: design-flow
description: Plan, build, redesign, polish, and review interfaces using bundled design specialists. Combines UI/UX research, visual direction, design systems, frontend engineering, interaction, animation, accessibility, and QA. Also routes explicit video, native UI, and Vercel deployment requests to their specialists. Use for a complete design pass or a targeted design task.
---

# Design Flow

One workflow with the complete design-studio collection included. Select relevant original skills, read their full instructions, execute the requested work, and verify the result. The whole directory is the skill; SKILL.md alone is insufficient.

`<skill-root>` means the directory containing this file. Use Python 3.10+ (`python`, `python3`, or `py -3` as available). The static [catalog](CATALOG.md) supports discovery without Python.

## 1. Understand

Identify the task, user, stack, affected surfaces, and scope. Inspect project instructions, existing UI, components, tokens, brand assets, and relevant PRODUCT.md or DESIGN.md. Distinguish a new build, redesign, refinement, and review. Infer reasonable defaults; ask only when missing information materially changes the work. A focused fix does not need a full design exercise.

## 2. Discover

```text
python "<skill-root>/scripts/pack.py" search "<task words>"
python "<skill-root>/scripts/pack.py" list --source designer
python "<skill-root>/scripts/pack.py" locate <catalog-id>
```

Read the selected original SKILL.md and relevant references. Relative paths resolve from that original file's directory. Scripts, datasets, templates, assets, notices, and complete source trees are bundled. Duplicate platform manifests and development fixtures are retained but excluded from default search; use `list --all` to inspect them. Fixtures are not production workflows.

Also consider relevant skills exposed by the current agent or existing project skill directories. Respect a user-named specialist. Do not assume a Claude-specific Skill tool exists: reading original instructions and using available tools is the portable path.

## 3. Plan

Choose one primary workflow and only the supporting specialists needed. State the sequence briefly, then proceed within the authorized scope. Existing brand and task constraints take priority over generic aesthetic preferences. Reviews produce findings unless fixes are also requested.

| Phase | Bundled collections |
| --- | --- |
| Direction and visual refinement | Impeccable, Taste, Anthropic frontend-design, UI UX Pro Max |
| Research, flows, copy, systems, handoff | Designer Skills |
| Implementation and performance | Vercel, UI UX Pro Max, Emil |
| Interaction and motion | Emil, FrankX motion, Remotion |
| Review, accessibility, responsive QA | Designer Skills, Impeccable, Vercel, FrankX motion |

Use motion only when it benefits the task. Deployment and external service work require a user request or existing authorization; installing instructions does not authorize publishing.

## 4. Execute

Follow the complete original specialist instructions rather than a summary. Load further specialists only for distinct needs. Resolve conflicts by the brief, task purpose, accessibility, and project conventions. Preserve truthful content; label demonstration data. Reuse existing components and dependencies where suitable.

Read [PORTABILITY.md](PORTABILITY.md) before the first script-backed workflow. Resolve source directories with `locate`; map upstream hardcoded installation paths to those locations. Keep cwd at the user's project for helpers that operate on it.

```text
python "<skill-root>/scripts/pack.py" run <catalog-id> -- python "<skill-dir>/scripts/example.py" <arguments>
```

The runner expands `<skill-dir>`, `<repo-dir>`, and `<plugin-dir>` and scopes compatible environment variables to the child process. The example filename is illustrative; inspect actual scripts before invoking them.

Upstream hooks, MCP definitions, and custom agents are preserved but not automatically registered by reading Markdown. Use documented manual equivalents when possible. Report unavailable host features; never claim a hook or gate ran when it did not.

## 5. Verify

Run relevant existing project checks. Inspect rendered UI at representative sizes when tools are available; test changed interactions, keyboard paths, relevant errors, and reduced motion. Use a review specialist for a substantive build or redesign. Inspect animation over time; still images cannot establish motion quality. Fix material issues within scope and recheck affected paths.

For the pack itself, `python "<skill-root>/scripts/pack.py" verify` checks snapshot integrity. `doctor` reports executable availability, not complete runtime readiness.

## 6. Report

Briefly identify specialists used, meaningful changes, checks performed, and material remaining gaps. Separate observed results from assumptions and pending runtime checks. Do not commit or push unless asked.

## Reference

- [Catalog](CATALOG.md): every original manifest and its selector.
- [Coverage](COVERAGE.md): measured counts and inclusion boundaries.
- [Dependencies](DEPENDENCIES.md): skill dependencies and optional runtimes.
- [Portability](PORTABILITY.md): paths, host features, and installation targets.
- [Third-party notices](THIRD_PARTY_NOTICES.md): attribution and license locations.

Revisions and file hashes are pinned in `sources.lock.json`. The Anthropic source selects frontend-design; the seven other requested repositories are included in full, plus the declared Remotion dependency. Separately recommended third-party projects remain links, as requested.
