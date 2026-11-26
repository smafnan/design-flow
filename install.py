import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import uuid


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "skill" / "design-flow"
sys.dont_write_bytecode = True
sys.path.insert(0, str(SOURCE / "scripts"))
from pack import verify


def destination(args):
    if args.skills_dir:
        parent = args.skills_dir.expanduser().resolve()
    elif args.scope == "project":
        project = (args.project or Path.cwd()).expanduser().resolve()
        parent = project / (".claude" if args.agent == "claude" else ".agents") / "skills"
    elif args.agent == "claude":
        parent = Path(os.environ.get("CLAUDE_SKILLS_DIR", Path.home() / ".claude" / "skills")).expanduser().resolve()
    elif args.agent == "codex":
        parent = Path.home() / ".agents" / "skills"
    else:
        parent = Path.home() / ".gemini" / "config" / "skills"
    target = parent / "design-flow"
    if target.is_symlink() or (hasattr(target, "is_junction") and target.is_junction()):
        raise ValueError(f"Refusing to replace a linked directory: {target}")
    if target.resolve() == SOURCE.resolve() or SOURCE.resolve().is_relative_to(target.resolve()):
        raise ValueError("Destination contains the repository's source skill")
    if target.resolve().is_relative_to(SOURCE.resolve()):
        raise ValueError("Destination cannot be inside the source skill")
    return target


def backup(target):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    folder = target.parent / ".design-flow-backups" / f"{stamp}-{uuid.uuid4().hex[:8]}"
    folder.mkdir(parents=True)
    saved = folder / "design-flow"
    target.rename(saved)
    return saved


def main():
    parser = argparse.ArgumentParser(description="Install the complete Design Flow skill offline")
    parser.add_argument("--agent", choices=("claude", "codex", "antigravity"), default="claude")
    parser.add_argument("--scope", choices=("user", "project"), default="user")
    parser.add_argument("--project", type=Path)
    parser.add_argument("--skills-dir", type=Path)
    parser.add_argument("--replace", action="store_true", help="Back up an existing skill before replacement")
    parser.add_argument("--uninstall", action="store_true", help="Move the installed skill to a recoverable backup")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.project and args.scope != "project":
        parser.error("--project requires --scope project")
    target = destination(args)
    action = "Uninstall" if args.uninstall else "Install"
    print(f"{action}: {target}")
    if args.dry_run:
        return
    if args.uninstall:
        if not target.exists():
            print("No installed skill at this location.")
            return
        receipt = target / ".design-flow-install.json"
        if not receipt.is_file() or json.loads(receipt.read_text(encoding="utf-8")).get("pack") != "design-flow":
            raise ValueError("No Design Flow installation receipt. Manage this older/manual installation explicitly.")
        print(f"Moved installation to recoverable backup: {backup(target)}")
        return
    if target.exists() and not args.replace:
        raise FileExistsError(f"Already exists: {target}. Use --replace to preserve it in a backup and install the new pack.")
    report = verify(SOURCE)
    if not report["ok"]:
        raise ValueError(f"Source integrity failed: {report['failures'][:5]}")
    if not (SOURCE / "catalog.json").is_file():
        raise ValueError("Missing catalog.json; run tools/build_catalog.py in the repository")
    target.parent.mkdir(parents=True, exist_ok=True)
    saved = None
    with tempfile.TemporaryDirectory(prefix=".design-flow-stage-", dir=target.parent) as temporary:
        stage = Path(temporary) / "design-flow"
        shutil.copytree(SOURCE, stage, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        report = verify(stage)
        if not report["ok"]:
            raise ValueError(f"Copied payload failed verification: {report['failures'][:5]}")
        for entry in json.loads((stage / "sources.lock.json").read_text(encoding="utf-8"))["sources"]:
            if os.name != "nt":
                for original in entry["files"]:
                    if "link" not in original:
                        (stage / ".upstream" / entry["id"] / original["path"]).chmod(original["mode"] & 0o777 or 0o644)
        (stage / ".design-flow-install.json").write_text(json.dumps({"pack": "design-flow", "schema_version": 1, "agent": args.agent}) + "\n", encoding="utf-8")
        if target.exists():
            saved = backup(target)
        try:
            stage.rename(target)
        except OSError:
            if saved and not target.exists():
                saved.rename(target)
            raise
    print(f"Installed and verified {report['checked']} upstream entries.")
    if saved:
        print(f"Previous installation preserved at: {saved}")
    print("Load a new agent session and invoke design-flow.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError) as error:
        print(f"Install failed: {error}", file=sys.stderr)
        sys.exit(1)
