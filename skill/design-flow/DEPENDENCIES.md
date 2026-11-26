# Dependencies

Installing Design Flow copies all bundled skill resources. Python 3.10+ is required for the installer, catalog search, script runner, and integrity checks. No pip packages are required for normal installation or use. Rebuilding the generated catalog uses the pinned PyYAML package in the repository's requirements-build.txt.

## Declared skill dependency

The motion collection's skills-lock.json declares `remotion-best-practices` from `remotion-dev/skills`. Its complete repository snapshot is included, along with its specialist skills and references. `dependencies.lock.json` records the original declaration and the resolved catalog ID.

The declaration refers to an older `skills/remotion` path. The pinned dependency now uses `skills/remotion-best-practices`; resolution is by skill name. The upstream legacy computedHash is retained as provenance, not asserted to match the newer pinned snapshot.

## Optional runtime requirements

| Collection | Conditional requirements |
| --- | --- |
| Impeccable | Bundled launcher, platform-specific engine, browser for visual inspection |
| Taste | Compatible Node and Chrome/Edge/Chromium; network for asset discovery; optional ffmpeg |
| UI UX Pro Max | Python for data search and system generation; chosen project stack |
| Anthropic frontend-design | The target project's development tools |
| Emil | Target web/native stack and chosen animation libraries |
| FrankX motion | Selected animation/video runtime and any authenticated media provider |
| Vercel | Target framework; CLI or authenticated connector for requested deployment and optimization |
| Designer Skills | Research evidence and task-appropriate design tools |
| Remotion | Compatible Node/React/Remotion, rendering tooling, and applicable licensing |

Exact requirements remain in original manifests and documentation. The installer does not execute upstream install scripts, install every framework globally, connect accounts, enable hooks, or start services. `doctor` reports available executables; it does not certify compatible versions, authentication, or runtime behavior.
