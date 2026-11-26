import ast
from collections import Counter
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skill" / "design-flow"
sys.dont_write_bytecode = True
sys.path.insert(0, str(SKILL / "scripts"))
from pack import contained, file_hash, locate, read_json, search, verify


def main():
    result = verify(SKILL)
    if not result["ok"]:
        raise ValueError(result["failures"])
    entries = read_json("catalog.json", SKILL)["entries"]
    actual = {path.relative_to(SKILL).as_posix() for path in (SKILL / ".upstream").rglob("SKILL.md")}
    if actual != {entry["path"] for entry in entries}:
        raise ValueError("Catalog coverage differs from bundled skill files")
    if len({entry["id"] for entry in entries}) != len(entries):
        raise ValueError("Duplicate catalog IDs")
    for entry in entries:
        if file_hash(contained(SKILL, entry["path"])) != entry["sha256"]:
            raise ValueError(f"Catalog hash mismatch: {entry['id']}")
        if entry["status"] == "active" and (not entry["description"] or entry["metadata_warning"]):
            raise ValueError(f"Unusable metadata: {entry['id']}")
        if entry.get("canonical_id"):
            canonical = locate(entry["canonical_id"], SKILL)
            if canonical["status"] != "active":
                raise ValueError(f"Invalid canonical target: {entry['id']}")
    for dependency in read_json("dependencies.lock.json", SKILL)["dependencies"]:
        if locate(dependency["resolved_id"], SKILL)["name"] != dependency["name"]:
            raise ValueError("Declared dependency is not resolved")
    for resource in read_json("resources.json", SKILL)["resources"]:
        if not contained(SKILL, resource["path"]).is_file():
            raise ValueError(f"Missing resource: {resource['path']}")
    for path in [ROOT / "install.py", *list((ROOT / "tools").glob("*.py")), *list((SKILL / "scripts").glob("*.py"))]:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for path in [ROOT / "README.md", *list((ROOT / "docs").glob("*.md")), *list(SKILL.glob("*.md"))]:
        for match in re.finditer(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            reference = match.group(1).split("#", 1)[0]
            if reference and not re.match(r"https?://", reference):
                if not (path.parent / reference).exists():
                    raise ValueError(f"Broken link in {path.name}: {reference}")
    if not any(entry["source"] == "taste" for entry in search("photographs", root=SKILL)):
        raise ValueError("Multiline Taste description was not indexed")
    if any(entry["status"] != "active" for entry in search("", root=SKILL)):
        raise ValueError("Default discovery exposed variants or development fixtures")
    print(json.dumps({"ok": True, "upstream_entries_verified": result["checked"],
                      "catalog_manifests": len(entries), "statuses": dict(Counter(entry["status"] for entry in entries)),
                      "sources": len(read_json("sources.lock.json", SKILL)["sources"])}, indent=2))


if __name__ == "__main__":
    main()
