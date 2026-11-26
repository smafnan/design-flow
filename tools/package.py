import argparse
import hashlib
from pathlib import Path
import sys
import zipfile


ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
from validate import main as validate


def main():
    parser = argparse.ArgumentParser(description="Build an offline Design Flow distribution")
    parser.add_argument("--output", type=Path, default=ROOT / "dist" / "design-flow.zip")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite {output}")
    validate()
    files = [ROOT / name for name in ("README.md", "LICENSE", "install.py", "install.sh", "install.ps1", "sources.json", "requirements-build.txt", ".gitattributes", ".gitignore")]
    for folder in ("skill", "tools", "docs", "assets"):
        files.extend(path for path in (ROOT / folder).rglob("*") if path.is_file()
                     and "__pycache__" not in path.parts and path.suffix != ".pyc")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(files):
            archive.write(path, "design-flow/" + path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise ValueError("ZIP integrity check failed")
        if len(archive.infolist()) != len(files):
            raise ValueError("Distribution file count mismatch")
        for path in files:
            bundled = archive.read("design-flow/" + path.relative_to(ROOT).as_posix())
            if hashlib.sha256(bundled).digest() != hashlib.sha256(path.read_bytes()).digest():
                raise ValueError(f"ZIP content mismatch: {path}")
    checksum = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(output.suffix + ".sha256").write_text(f"{checksum}  {output.name}\n", encoding="utf-8")
    print(f"Packaged and verified {len(files)} files: {output} ({output.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
