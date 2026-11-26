# Coverage

Pinned snapshots of the eight requested sources plus declared skill dependencies. Counts are measured from included files, not repository marketing pages. Active means the default selectable workflow; platform variants remain available with --all.

| Source | Original files | Active | Variants | Duplicates | Development | Revision |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| impeccable | 5034 | 1 | 22 | 0 | 4 | `2fc5e1459efbbf06d92c7306517c286bf12490cf` |
| taste | 1664 | 1 | 0 | 0 | 0 | `d1a2bb41d927083ac7118f60cfc9cdf711810ea0` |
| ui-ux-pro-max | 753 | 7 | 0 | 6 | 0 | `b73ee96f8d4ff7bbc279c52dadcd907ffe23629c` |
| anthropic | 3 | 1 | 0 | 0 | 0 | `e4bb5d960d87126ff3b3a8af1a104b7db67560ba` |
| emil | 36 | 20 | 0 | 0 | 0 | `64eb3deb9a5fbfa041faf783e0bc3fd635872e9c` |
| motion | 65 | 5 | 0 | 0 | 0 | `e7dc6e2e728c918ffcea5edb2d7c94e2a6f7785d` |
| vercel | 445 | 9 | 0 | 0 | 0 | `5a37a6329fbad3666c3207392a6a7c0110e92efb` |
| designer | 205 | 111 | 0 | 0 | 0 | `9a6930cf84a822eb458624bd11c61aac5bbdf224` |
| remotion | 271 | 14 | 0 | 0 | 0 | `a3f4098a2afd0e13f6a6f8c8760e275f75457ea9` |

## Inclusion rules

- The seven requested repository roots and the declared dependency repository are included in full. Vercel deployment/cost workflows, native skills, scripts, datasets, commands, templates, and support files are retained.
- The Anthropic file URL selects frontend-design. Its complete skill directory and available root notices are included; unrelated Anthropic skills are outside the requested source.
- Declared GitHub skill dependencies in skills-lock.json are bundled. Remotion now uses skills/remotion-best-practices instead of its declaration's older skills/remotion path; resolution is by skill name. The legacy computedHash is recorded, not asserted to match the newer pinned revision.
- Recommended third-party projects remain links rather than recursively installed dependencies, as requested.
- Exact-byte duplicates and nonidentical platform variants share a default catalog selection. All original manifests and adjacent resources remain individually addressable by ID with --all.
- Development fixtures are retained and indexed, but not advertised as user workflows.
- Source completeness does not mean every optional runtime, host hook, paid service, or account-dependent workflow has been installed or executed.

Total: 201 skill manifests; 169 default selectable workflows; 3303 indexed supporting resources.
