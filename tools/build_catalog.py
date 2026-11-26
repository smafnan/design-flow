import collections
import hashlib
import json
from pathlib import Path
import re
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skill" / "design-flow"
sys.path.insert(0, str(SKILL / "scripts"))
from pack import file_hash


def write_json(name, data):
    (SKILL / name).write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def slug(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "unnamed"


def metadata(path):
    content = path.read_text(encoding="utf-8-sig")
    if not content.startswith("---"):
        return {}, "No YAML frontmatter"
    sections = re.split(r"^---\s*$", content, maxsplit=2, flags=re.MULTILINE)
    if len(sections) != 3:
        return {}, "Unclosed YAML frontmatter"
    try:
        result = yaml.safe_load(sections[1])
        return (result, None) if isinstance(result, dict) else ({}, "Frontmatter is not a mapping")
    except yaml.YAMLError as error:
        return {}, str(error)


def priority(entry):
    path = entry["path"]
    return (0 if "/.agents/skills/" in path else 1 if "/skills/" in path and "/cli/" not in path else 2,
            len(path), path)


def main():
    lock = json.loads((SKILL / "sources.lock.json").read_text(encoding="utf-8"))
    entries = []
    resources = []
    notices = []
    dependency_records = []
    repositories = {source["repo"].lower(): source["id"] for source in lock["sources"]}
    for source in lock["sources"]:
        repo_root = SKILL / ".upstream" / source["id"]
        for original in source["files"]:
            path = repo_root / original["path"]
            if "link" not in original and (not path.is_file() or file_hash(path) != original["sha256"]):
                raise ValueError(f"Original file missing or modified: {path}")
        for path in sorted(repo_root.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(SKILL).as_posix()
            name = path.name.lower()
            if any(word in name for word in ("license", "notice", "copying", "ofl")):
                notices.append({"source": source["id"], "path": relative})
            if path.name == "skills-lock.json":
                declared = json.loads(path.read_text(encoding="utf-8"))
                for dependency_name, dependency in declared.get("skills", {}).items():
                    repo = dependency.get("source", "").lower()
                    target = repositories.get(repo)
                    if not target:
                        raise ValueError(f"Unbundled declared skill dependency: {dependency_name} from {repo}")
                    dependency_records.append({"name": dependency_name, "declared_by": relative,
                                               "source": target, "declaration": dependency})
            if path.name == ".gitmodules":
                raise ValueError(f"Submodule requires explicit vendoring: {path}")
            if path.name == "SKILL.md":
                frontmatter, error = metadata(path)
                skill_name = str(frontmatter.get("name") or path.parent.name)
                description = str(frontmatter.get("description") or f"Original {skill_name} instructions from {source['repo']}")
                development = bool(set(path.relative_to(repo_root).parts) & {"test", "tests", "fixtures", "examples"})
                entries.append({"source": source["id"], "name": skill_name,
                                "description": " ".join(description.split()), "path": relative,
                                "sha256": file_hash(path), "status": "development" if development else "active",
                                "license": frontmatter.get("license"),
                                "host_features": [key for key in ("hooks", "context", "agent", "allowed-tools", "disable-model-invocation") if key in frontmatter],
                                "metadata_warning": error})
            elif (path.suffix.lower() in (".csv", ".json", ".yaml", ".yml", ".py", ".js", ".mjs", ".sh", ".cmd", ".ps1")
                  or any(part in path.parts for part in ("commands", "workflows", "agents"))):
                resources.append({"source": source["id"], "path": relative})
    seen_hashes = {}
    seen_names = {}
    used_ids = set()
    used_names = set()
    for entry in sorted(entries, key=priority):
        base = f"{entry['source']}/{slug(entry['name'])}"
        identifier = base
        if identifier in used_ids:
            identifier += "-" + hashlib.sha256(entry["path"].encode()).hexdigest()[:8]
        entry["id"] = identifier
        used_ids.add(identifier)
        install_name = "ds-" + slug(identifier)
        if len(install_name) > 63:
            install_name = install_name[:54] + "-" + hashlib.sha256(identifier.encode()).hexdigest()[:8]
        if install_name in used_names:
            raise ValueError(f"Install name collision: {install_name}")
        entry["install_name"] = install_name
        used_names.add(install_name)
        key = (entry["source"], entry["sha256"])
        if entry["status"] == "active":
            if key in seen_hashes:
                entry["status"] = "duplicate"
                entry["canonical_id"] = seen_hashes[key]
            elif (entry["source"], entry["name"]) in seen_names:
                entry["status"] = "variant"
                entry["canonical_id"] = seen_names[(entry["source"], entry["name"])]
            else:
                seen_hashes[key] = identifier
                seen_names[(entry["source"], entry["name"])] = identifier
    entries.sort(key=lambda entry: entry["id"])
    for dependency in dependency_records:
        matches = [entry for entry in entries if entry["source"] == dependency["source"] and entry["name"] == dependency["name"]]
        if not matches:
            raise ValueError(f"Declared skill missing: {dependency['name']}")
        dependency["resolved_id"] = matches[0]["id"]
        dependency["resolved_path"] = matches[0]["path"]
    write_json("catalog.json", {"schema_version": 1, "entries": entries})
    write_json("resources.json", {"schema_version": 1, "resources": resources})
    write_json("dependencies.lock.json", {"schema_version": 1, "dependencies": dependency_records})
    catalog = ["# Complete Skill Catalog", "", "All original manifests are listed. Active entries are selectable through design-flow. Exact-byte duplicate platform manifests and development fixtures remain fully bundled and directly addressable. IDs are catalog selectors, not separately installed slash commands.", ""]
    coverage = ["# Coverage", "", "Pinned snapshots of the eight requested sources plus declared skill dependencies. Counts are measured from included files, not repository marketing pages. Active means the default selectable workflow; platform variants remain available with --all.", "", "| Source | Original files | Active | Variants | Duplicates | Development | Revision |", "| --- | ---: | ---: | ---: | ---: | ---: | --- |"]
    notice_lines = ["# Third-Party Notices", "", "Upstream source files are preserved unchanged. Symlinks are materialized as copies for Windows portability; their original targets are recorded in sources.lock.json. Pack-authored routing, indexing, and installation files are separate. No blanket license is assigned to the upstream collections.", "", "## Provenance", ""]
    for source in lock["sources"]:
        selected = [entry for entry in entries if entry["source"] == source["id"]]
        counts = collections.Counter(entry["status"] for entry in selected)
        coverage.append(f"| {source['id']} | {len(source['files'])} | {counts['active']} | {counts['variant']} | {counts['duplicate']} | {counts['development']} | `{source['commit']}` |")
        catalog.extend([f"## {source['id']}", "", f"Source: https://github.com/{source['repo']}/tree/{source['commit']}", ""])
        for entry in selected:
            catalog.extend([f"### {entry['id']}", "", f"Status: {entry['status']}.", "", entry["description"], "", f"[Original instructions]({entry['path']})", ""])
        notice_lines.extend([f"### {source['id']}", "", f"Repository: https://github.com/{source['repo']}/tree/{source['commit']}", ""])
        license_files = [notice for notice in notices if notice["source"] == source["id"]]
        for notice in license_files:
            notice_lines.append(f"- [{notice['path']}]({notice['path']})")
        if not license_files:
            notice_lines.append("No standalone license/notice file was present in this snapshot. Preserve per-skill license declarations where present; public redistribution terms need confirmation from upstream. Inclusion in this personal pack is not a licensing grant.")
        notice_lines.append("")
    coverage.extend([
        "", "## Inclusion rules", "",
        "- The seven requested repository roots and the declared dependency repository are included in full. Vercel deployment/cost workflows, native skills, scripts, datasets, commands, templates, and support files are retained.",
        "- The Anthropic file URL selects frontend-design. Its complete skill directory and available root notices are included; unrelated Anthropic skills are outside the requested source.",
        "- Declared GitHub skill dependencies in skills-lock.json are bundled. Remotion now uses skills/remotion-best-practices instead of its declaration's older skills/remotion path; resolution is by skill name. The legacy computedHash is recorded, not asserted to match the newer pinned revision.",
        "- Recommended third-party projects remain links rather than recursively installed dependencies, as requested.",
        "- Exact-byte duplicates and nonidentical platform variants share a default catalog selection. All original manifests and adjacent resources remain individually addressable by ID with --all.",
        "- Development fixtures are retained and indexed, but not advertised as user workflows.",
        "- Source completeness does not mean every optional runtime, host hook, paid service, or account-dependent workflow has been installed or executed.", "",
        f"Total: {len(entries)} skill manifests; {sum(entry['status'] == 'active' for entry in entries)} default selectable workflows; {len(resources)} indexed supporting resources.", ""
    ])
    (SKILL / "CATALOG.md").write_text("\n".join(catalog), encoding="utf-8")
    (SKILL / "COVERAGE.md").write_text("\n".join(coverage), encoding="utf-8")
    (SKILL / "THIRD_PARTY_NOTICES.md").write_text("\n".join(notice_lines), encoding="utf-8")
    print(coverage[-2])


if __name__ == "__main__":
    main()
