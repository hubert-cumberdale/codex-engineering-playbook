#!/usr/bin/env bash
set -euo pipefail

repo_root=$(git rev-parse --show-toplevel 2>/dev/null || true)
if [[ -z "$repo_root" ]]; then
  echo "[review-checks] Unable to locate git repository root."
  exit 2
fi

hook_source="$repo_root/scripts/pre-push"
hook_target="$repo_root/.git/hooks/pre-push"

if [[ ! -f "$hook_source" ]]; then
  echo "[review-checks] Hook source not found: $hook_source"
  exit 2
fi

mkdir -p "$repo_root/.git/hooks"
cp "$hook_source" "$hook_target"
chmod +x "$hook_target"

echo "[review-checks] Installed pre-push hook at $hook_target"
echo "[review-checks] To uninstall: rm $hook_target"
