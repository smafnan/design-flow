# Maintaining the bundled collection

## Validate a checkout

```sh
python tools/validate.py
python skill/design-flow/scripts/pack.py verify
```

Validation checks original file hashes, the materialized upstream symlink, complete catalog coverage, canonical selectors, dependency resolution, supporting resource paths, pack-authored Python syntax, local documentation links, and discovery behavior. It does not execute every upstream workflow or establish host-app compatibility.

## Rebuild generated metadata

```sh
python -m pip install -r requirements-build.txt
python tools/build_catalog.py
python tools/validate.py
```

The committed catalog is parsed with PyYAML at build time, so multiline frontmatter remains searchable. Normal users do not need PyYAML. Default selection uses one entry per source/name; byte-identical duplicates, nonidentical platform variants, and development fixtures stay in the full catalog.

## Refresh a snapshot

Sources are pinned by commit in sources.json. sources.lock.json records archive and per-file hashes. The vendor helper refuses to overwrite an existing source tree or replace a pinned revision in place.

For an update, use a fresh staging copy of the repository's pack-authored files and the updated sources.json, without .upstream or sources.lock.json. Run `python tools/vendor.py --cache <download-cache>` in that staging copy, then rebuild and validate its catalog. Review upstream licenses, dependency declarations, changed helpers, and generated metadata before replacing the corresponding snapshot and lock in your working repository. Preserve the old snapshot until the new one validates.

The helper downloads archives only; it does not execute upstream code. Re-run catalog generation whenever source revisions change. New declared GitHub skill dependencies must be added to sources.json and vendored; unresolved dependencies make the catalog build fail.

## Git and original bytes

Vendored files retain their original .gitignore files. When preparing an explicitly requested commit, force-add the vendored tree so upstream ignore rules cannot silently omit bundled files:

```sh
git add -f -- skill/design-flow/.upstream
git add -- README.md LICENSE .gitignore .gitattributes install.py install.sh install.ps1 sources.json requirements-build.txt tools docs skill/design-flow
```

Do not apply line-ending normalization or formatting to .upstream. The root .gitattributes disables text conversion for this tree. Review the staged snapshot before committing; retaining a file locally is not sufficient if it is omitted from the Git index. Validate a fresh checkout after publishing.

One pack-authored Git attribute overlay lives at `.upstream/ui-ux-pro-max/src/ui-ux-pro-max/data/.gitattributes`. It preserves the original CRLF bytes of `catalog-summary.json`, overriding the upstream parent's normalization rule without changing either original file. Retain this overlay when refreshing that snapshot, unless the new source no longer needs it. It is integration metadata, not an upstream entry in sources.lock.json.

## Build a portable distribution

```sh
python tools/package.py
```

This creates dist/design-flow.zip and its SHA-256 sidecar. It includes the complete skill directory, installers, source manifest, maintenance tools, documentation, and README assets. It excludes .git, local .impeccable state, and Python caches. Every archived file is compared with the source before success is reported. Existing output archives are never overwritten.

## Licenses and publication

The root MIT license covers original Design Flow work. Bundled source content retains its upstream terms; see the generated [notices](../skill/design-flow/THIRD_PARTY_NOTICES.md). The Vercel and Remotion snapshots do not include a standalone repository license file. Some Vercel skills declare MIT in frontmatter; that does not establish the terms of every bundled file. Confirm applicable redistribution terms before publishing the complete bundle. Do not label the whole vendored collection MIT or remove notices.
