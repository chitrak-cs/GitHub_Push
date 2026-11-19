#!/usr/bin/env bash
# Install ghpush as a command by linking it into ~/.local/bin.
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/ghpush.py"
BIN="${HOME}/.local/bin"

chmod +x "$SRC"
mkdir -p "$BIN"
ln -sf "$SRC" "$BIN/ghpush"
echo "✔ Linked $BIN/ghpush -> $SRC"

case ":$PATH:" in
  *":$BIN:"*) echo "✔ $BIN is on your PATH — try: ghpush --help" ;;
  *) echo "⚠ $BIN is not on your PATH. Add this to ~/.bashrc:"
     echo "    export PATH=\"\$HOME/.local/bin:\$PATH\"" ;;
esac

command -v gh >/dev/null || echo "⚠ GitHub CLI not found: sudo apt install gh"
