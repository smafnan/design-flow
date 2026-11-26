import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def read_json(name, root=ROOT):
    return json.loads((root / name).read_text(encoding="utf-8"))


def contained(root, relative):
    target = (root / relative).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError(f"Path outside pack: {relative}")
    return target


def file_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(root=ROOT):
    failures = []
    lock = read_json("sources.lock.json", root)
    checked = 0
    for source in lock["sources"]:
        repo_root = contained(root, f".upstream/{source['id']}")
        for entry in source["files"]:
            if "link" in entry:
                target = contained(repo_root, entry["path"])
                original = contained(repo_root, str(target.parent.relative_to(repo_root) / entry["link"]))
                checked += 1
                if not target.is_file() or not original.is_file() or file_hash(target) != file_hash(original):
                    failures.append(f"Invalid materialized link: {source['id']}/{entry['path']}")
                continue
            target = contained(repo_root, entry["path"])
            checked += 1
            if not target.is_file():
                failures.append(f"Missing: {source['id']}/{entry['path']}")
            elif file_hash(target) != entry["sha256"]:
                failures.append(f"Changed: {source['id']}/{entry['path']}")
    return {"ok": not failures, "checked": checked, "failures": failures}


def select(identifier, root=ROOT):
    entries = read_json("catalog.json", root)["entries"]
    matches = [entry for entry in entries if entry["id"] == identifier or entry["install_name"] == identifier]
    if not matches:
        matches = [entry for entry in entries if entry["name"] == identifier and entry["status"] == "active"]
    if len(matches) != 1:
        raise ValueError(f"Expected one match for {identifier!r}; found {len(matches)}. Use a catalog ID.")
    return matches[0]


def locate(identifier, root=ROOT):
    entry = select(identifier, root)
    skill_file = contained(root, entry["path"])
    repo_dir = contained(root, f".upstream/{entry['source']}")
    plugin_dir = repo_dir
    for ancestor in (skill_file.parent, *skill_file.parent.parents):
        if not ancestor.is_relative_to(repo_dir):
            break
        if (ancestor / ".claude-plugin" / "plugin.json").is_file():
            plugin_dir = ancestor
            break
    return dict(entry, skill_file=str(skill_file), skill_dir=str(skill_file.parent),
                repo_dir=str(repo_dir), plugin_dir=str(plugin_dir))


def search(query, source=None, include_all=False, root=ROOT):
    tokens = re.findall(r"[a-z0-9]+", query.lower())
    results = []
    entries = read_json("catalog.json", root)["entries"]
    for entry in entries:
        if source and entry["source"] != source:
            continue
        if not include_all and entry["status"] != "active":
            continue
        name = f"{entry['source']} {entry['name']}".lower()
        description = entry["description"].lower()
        score = sum(10 * (token in name) + 2 * (token in description) for token in tokens)
        score += 20 * (query.lower() == entry["name"].lower())
        if not tokens or score:
            results.append((score, entry))
    return [entry for score, entry in sorted(results, key=lambda result: (-result[0], result[1]["id"]))]


def run(identifier, command, root=ROOT):
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        raise ValueError("Supply an executable and arguments after --")
    location = locate(identifier, root)
    replacements = {"<skill-dir>": location["skill_dir"], "<repo-dir>": location["repo_dir"],
                    "<plugin-dir>": location["plugin_dir"]}
    expanded = []
    for argument in command:
        for token, value in replacements.items():
            argument = argument.replace(token, value)
        expanded.append(argument)
    environment = os.environ.copy()
    environment.update(CLAUDE_SKILL_DIR=location["skill_dir"], CLAUDE_PLUGIN_ROOT=location["plugin_dir"],
                       CLAUDE_PROJECT_DIR=str(Path.cwd()), DESIGN_STUDIO_SKILL_DIR=location["skill_dir"],
                       DESIGN_STUDIO_REPO_DIR=location["repo_dir"])
    return subprocess.run(expanded, env=environment, check=False).returncode


def doctor():
    commands = ("python", "python3", "node", "npm", "bun", "bash", "git", "ffmpeg", "vercel", "google-chrome", "chromium")
    return {"python_running": sys.version.split()[0], "executables": {command: shutil.which(command) for command in commands},
            "note": "Availability only; optional runtimes, browser versions, accounts, and host hooks are not validated. See DEPENDENCIES.md."}


def main():
    parser = argparse.ArgumentParser(description="Discover and use every bundled design specialist")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("search", "list"):
        child = subparsers.add_parser(name)
        if name == "search":
            child.add_argument("query")
            child.add_argument("--limit", type=int, default=12)
        child.add_argument("--source")
        child.add_argument("--all", action="store_true")
        child.add_argument("--json", action="store_true")
    for name in ("locate", "show"):
        child = subparsers.add_parser(name)
        child.add_argument("id")
    child = subparsers.add_parser("run")
    child.add_argument("id")
    child.add_argument("argv", nargs=argparse.REMAINDER)
    subparsers.add_parser("verify")
    subparsers.add_parser("doctor")
    args = parser.parse_args()
    try:
        if args.command in ("list", "search"):
            results = search(getattr(args, "query", ""), args.source, args.all)
            if args.command == "search":
                results = results[:args.limit]
            if args.json:
                print(json.dumps(results, indent=2, ensure_ascii=True))
            else:
                for entry in results:
                    print(f"{entry['id']} [{entry['status']}]\n  {entry['description']}\n  {ROOT / entry['path']}")
        elif args.command == "locate":
            print(json.dumps(locate(args.id), indent=2, ensure_ascii=True))
        elif args.command == "show":
            print(Path(locate(args.id)["skill_file"]).read_text(encoding="utf-8"))
        elif args.command == "run":
            return run(args.id, args.argv)
        elif args.command == "doctor":
            print(json.dumps(doctor(), indent=2))
        elif args.command == "verify":
            report = verify()
            print(json.dumps(report, indent=2))
            return 0 if report["ok"] else 1
    except (ValueError, OSError, KeyError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
