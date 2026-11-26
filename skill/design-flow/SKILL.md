---
name: design-flow
description: Orchestrates all installed design skills on the current project. Scans available skills, picks the right ones for the task (build, redesign, motion, review, accessibility, UX), then does the work and verifies it. Use when the user runs /design-flow or asks for a full design pass on a project.
argument-hint: "<what to design or improve, e.g. 'redesign the landing page' or 'polish dashboard'>"
---

# design-flow

Task from the user: $ARGUMENTS
(If empty, ask one short question: what should be designed or improved, and for whom.)

## Step 1: Understand the project (read-only, be quick)
- Detect stack: `package.json`, framework (Next/React/Vue/Svelte/Astro/plain HTML), Tailwind, component library, React Native/Expo/Swift.
- Look for existing design context: `DESIGN.md`, `PRODUCT.md`, design tokens, `tailwind.config.*`, global CSS, brand assets, a `.impeccable*` folder.
- Note the target: new build, redesign, or polish of existing UI. Note pages/components in scope.

## Step 2: Discover available design skills (do this every run, never assume)
Collect skills from both locations and read each one's frontmatter `name` and `description`:
```
for f in ~/.claude/skills/*/SKILL.md .claude/skills/*/SKILL.md; do
  [ -f "$f" ] && echo "$(basename $(dirname $f)): $(grep -m1 '^description:' $f | cut -c14-200)"
done
```
Keep only design-related ones (UI, UX, visual, motion, animation, accessibility, typography, color, layout, design system, frontend, critique, research). Ignore unrelated skills.

## Step 3: Pick a short plan (3-6 skills, not all)
Choose by phase. Prefer skills that exist; substitute if one is missing.
1. **Direction**: `taste-skill`, `impeccable`, `frontend-design`, `ui-ux-pro-max` (pick ONE primary art-direction skill; use others only to fill gaps). For a new design system also `design-token`, `color-system`, `typography-scale`, `spacing-system`.
2. **Build**: the primary skill from phase 1, plus stack skills: `react-best-practices`, `composition-patterns` (React/Next), `ui-styling` (Tailwind/shadcn), `mobile-native` or `animate-expo` (mobile), `responsive-design`, `form-design`, `loading-states` as needed.
3. **Motion** (only if the task or product benefits): `animate`, `choreograph`, `gestures`, `react-view-transitions`, `motion-director`.
4. **Review**: `web-design-guidelines`, `break-ui`, `review-animations`, `web-motion-auditor`, `critique-visual-hierarchy`, `critique-typography`, `critique-color`, `critique-composition`.
5. **Accessibility and UX**: `accessibility-audit`, `heuristic-evaluation`, `ux-writing`.

Tell the user the plan in 3-5 lines: which skills, in what order, and why. Then proceed without waiting unless the scope is ambiguous or the change is large (many files, deleting existing design). In that case confirm first.

## Step 4: Execute
- Invoke each chosen skill with the Skill tool, in order, and follow its instructions for this project.
- Resolve conflicts explicitly: one art-direction skill leads; others must not contradict it. Existing brand/tokens win over generic taste.
- Match the project's stack and conventions. Reuse existing components and tokens. Do not add dependencies without saying so.
- Use real content or clearly marked placeholders. Never invent customer data.

## Step 5: Verify
- Run the project's build/lint/tests if present.
- If a dev server and browser tools are available, view the result at mobile and desktop widths and check for broken layout, contrast, focus states, and reduced-motion behavior.
- Run at least one review-phase skill on the result and fix material issues.

## Step 6: Report (short)
- Skills used and what each contributed.
- Files changed.
- What was verified and what was not (be honest if something could not be checked).
- 2-3 suggested next steps.

## Rules
- Do not commit or push unless the user asks.
- Do not run every design skill; over-applying produces inconsistent results.
- If no design skills are installed, say so and proceed with general good practice.
