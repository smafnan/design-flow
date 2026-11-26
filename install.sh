#!/usr/bin/env sh
# Installs the design-flow skill globally for Claude Code (macOS, Linux, Git Bash).
set -e
SRC="$(cd "$(dirname "$0")" && pwd)/skill/design-flow"
DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}/design-flow"

if [ "$1" = "--uninstall" ]; then
  rm -rf "$DEST"
  echo "Removed $DEST"
  exit 0
fi

mkdir -p "$(dirname "$DEST")"
rm -rf "$DEST"
cp -r "$SRC" "$DEST"
echo "Installed design-flow to $DEST"
echo "Restart Claude Code, then run: /design-flow <what you want>"
