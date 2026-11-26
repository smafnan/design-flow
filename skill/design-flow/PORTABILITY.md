# Portability and runtime paths

Design Flow uses the standard SKILL.md format. Install its complete folder; the router locates specialists inside `.upstream/`. It reads original instructions rather than requiring a platform-specific Skill tool. The install and discovery utilities use only Python 3.10+ standard-library modules.

## Resolve paths before running tools

`python scripts/pack.py locate <id>` returns `skill_dir`, `repo_dir`, and `plugin_dir`. Relative references resolve from the original skill directory. The plugin directory is the nearest ancestor containing `.claude-plugin/plugin.json`, or the upstream repository root when none is present.

The runner expands literal `<skill-dir>`, `<repo-dir>`, and `<plugin-dir>` arguments and supplies `CLAUDE_SKILL_DIR`, `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PROJECT_DIR`, `DESIGN_STUDIO_SKILL_DIR`, and `DESIGN_STUDIO_REPO_DIR` to its child process. It preserves the current working directory and does not invoke a shell implicitly. For a shell script, invoke its required shell explicitly.

```text
python "<skill-root>/scripts/pack.py" run ui-ux-pro-max/ui-ux-pro-max -- python "<skill-dir>/scripts/search.py" "accessible forms" --domain ux
```

Some upstream text assumes `.claude/skills/...` or `.agents/skills/...`. Substitute the exact bundled locations from `locate`; do not create a second installation merely to satisfy a textual path. A helper that hardcodes paths internally may require its native installation or a dedicated adapter. Report that limitation rather than changing the preserved original.

## Host-specific features

| Feature | Behavior in this pack |
| --- | --- |
| Instructions, references, datasets, templates, assets | Included and locally accessible |
| Python, Node, shell helpers | Included; their runtime and library requirements still apply |
| Impeccable engine | Launcher included; platform-specific binary may download on first use |
| Claude hooks and dynamic frontmatter substitutions | Preserved in originals; reading the file does not register them |
| Plugin hooks, custom agents, MCP configuration | Preserved, but not merged into host settings by the installer |
| Browsers, authenticated services, rendering tools | Supplied by the host or installed separately as needed |

Use documented manual equivalents for host hooks when possible. A missing host API is a functional limitation, not a reason to claim the native behavior is active. `doctor` checks executable availability only.

## Installation locations

| Target | User scope | Project scope |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/design-flow` | `.claude/skills/design-flow` |
| Codex | `~/.agents/skills/design-flow` | `.agents/skills/design-flow` |
| Antigravity | `~/.gemini/config/skills/design-flow` | `.agents/skills/design-flow` |

Use `--skills-dir` for a supported alternative, such as this environment's `~/.codex/skills` or a legacy Antigravity path. Paths are relative to the selected project's root in project scope. Codex and Antigravity share a project destination; one copy is enough there.

The installer supports local agent environments, not direct uploads to Claude or Gemini chat websites. Gemini CLI discovery is not verified. Claude Code, Codex, and Antigravity installation paths follow their documentation; end-to-end behavior inside each application has not been tested.

Documentation checked 2026-11-26: [Claude Code](https://code.claude.com/docs/en/skills), [Codex](https://learn.chatgpt.com/docs/build-skills), [Antigravity](https://antigravity.google/docs/skills).
