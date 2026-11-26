import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import urllib.request
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skill" / "design-flow"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def included(path, source):
    return not source.get("include") or any(
        path == prefix or path.startswith(prefix) for prefix in source["include"]
    )


def safe_path(root, relative):
    parts = PurePosixPath(relative).parts
    if not parts or any(part in ("..", ".") or ":" in part or "\\" in part for part in parts):
        raise ValueError(f"Unsafe archive path: {relative}")
    target = root.joinpath(*parts)
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Archive escaped destination: {relative}")
    return target


def fetch(source, cache):
    archive = cache / f"{source['id']}-{source['commit']}.zip"
    url = f"https://codeload.github.com/{source['repo']}/zip/{source['commit']}"
    if not archive.exists():
        temporary = archive.with_suffix(".download")
        request = urllib.request.Request(url, headers={"User-Agent": "design-studio-pack-builder"})
        with urllib.request.urlopen(request, timeout=120) as response, temporary.open("wb") as output:
            shutil.copyfileobj(response, output)
        temporary.replace(archive)
    destination = SKILL / ".upstream" / source["id"]
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite snapshot: {destination}")
    destination.mkdir(parents=True)
    entries = []
    links = []
    with zipfile.ZipFile(archive) as bundle:
        prefix = bundle.infolist()[0].filename.split("/", 1)[0] + "/"
        for member in bundle.infolist():
            if member.is_dir():
                continue
            if not member.filename.startswith(prefix):
                raise ValueError("Mixed archive roots")
            relative = member.filename[len(prefix):]
            if not included(relative, source):
                continue
            target = safe_path(destination, relative)
            data = bundle.read(member)
            mode = member.external_attr >> 16
            entry = {"path": relative, "sha256": digest(data), "size": len(data), "mode": mode}
            if stat.S_ISLNK(mode):
                entry["link"] = data.decode("utf-8")
                links.append((target, entry))
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                if os.name != "nt":
                    target.chmod(mode & 0o777 or 0o644)
            entries.append(entry)
        for target, entry in links:
            source_path = (target.parent / entry["link"]).resolve()
            if not source_path.is_relative_to(destination.resolve()) or not source_path.exists():
                raise ValueError(f"Unresolved or external symlink: {target} -> {entry['link']}")
            target.parent.mkdir(parents=True, exist_ok=True)
            if source_path.is_dir():
                shutil.copytree(source_path, target)
                entry["materialized"] = "directory"
            else:
                shutil.copy2(source_path, target)
                entry["materialized"] = "file"
    result = dict(source, archive_url=url, archive_sha256=digest(archive.read_bytes()), files=entries)
    print(f"Vendored {source['id']}: {len(entries)} original files, {archive.stat().st_size:,} archive bytes", flush=True)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", type=Path, required=True)
    args = parser.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    sources = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))["sources"]
    lock_path = SKILL / "sources.lock.json"
    previous = json.loads(lock_path.read_text(encoding="utf-8"))["sources"] if lock_path.exists() else []
    existing = {source["id"]: source for source in previous}
    pending = []
    for source in sources:
        if source["id"] in existing:
            if source["commit"] != existing[source["id"]]["commit"]:
                raise ValueError("Build updates in a fresh output directory; existing revisions are immutable")
        else:
            pending.append(source)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        fetched = list(executor.map(lambda source: fetch(source, args.cache), pending))
    existing.update({source["id"]: source for source in fetched})
    results = [existing[source["id"]] for source in sources]
    lock = {"schema_version": 1, "sources": results}
    (SKILL / "sources.lock.json").write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    print(f"Locked {len(results)} sources")


if __name__ == "__main__":
    main()
