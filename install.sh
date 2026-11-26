#!/usr/bin/env sh
set -eu
PACK_ROOT="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
if command -v python3 >/dev/null 2>&1; then
  exec python3 "$PACK_ROOT/install.py" "$@"
elif command -v python >/dev/null 2>&1; then
  exec python "$PACK_ROOT/install.py" "$@"
else
  printf '%s\n' 'Python 3.10 or newer is required.' >&2
  exit 1
fi
