#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILL_NAME="reference-website-builder"
MODE="global"
PROJECT_PATH=""
DRY_RUN="false"

usage() {
  cat <<'EOF'
Usage:
  bash scripts/install.sh                         Install to ~/.agents/skills
  bash scripts/install.sh --project /path/repo   Install to <repo>/.agents/skills
  bash scripts/install.sh --legacy-codex         Install to ~/.codex/skills
  bash scripts/install.sh --dry-run               Show destination without copying
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project)
      MODE="project"
      PROJECT_PATH="${2:-}"
      [[ -n "$PROJECT_PATH" ]] || { echo "Missing project path" >&2; exit 2; }
      shift 2
      ;;
    --legacy-codex)
      MODE="legacy"
      shift
      ;;
    --dry-run)
      DRY_RUN="true"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

case "$MODE" in
  global)
    BASE_DIR="${HOME}/.agents/skills"
    ;;
  legacy)
    BASE_DIR="${HOME}/.codex/skills"
    ;;
  project)
    PROJECT_PATH="$(cd "$PROJECT_PATH" && pwd)"
    BASE_DIR="${PROJECT_PATH}/.agents/skills"
    ;;
esac

DEST="${BASE_DIR}/${SKILL_NAME}"

echo "Source:      $SKILL_ROOT"
echo "Destination: $DEST"

if [[ "$DRY_RUN" == "true" ]]; then
  exit 0
fi

mkdir -p "$BASE_DIR"

if [[ -e "$DEST" ]]; then
  BACKUP="${DEST}.backup-$(date +%Y%m%d-%H%M%S)"
  echo "Existing installation found; moving it to $BACKUP"
  mv "$DEST" "$BACKUP"
fi

mkdir -p "$DEST"
cp -R "$SKILL_ROOT"/. "$DEST"/
rm -rf "$DEST"/__pycache__ "$DEST"/scripts/__pycache__

python3 "$DEST/scripts/validate_skill.py" "$DEST"

echo
printf 'Installed %s\n' "$SKILL_NAME"
echo "Restart Codex or open a new session."
echo "If discovery is unreliable, add AGENTS_SNIPPET.md to the repository AGENTS.md."
