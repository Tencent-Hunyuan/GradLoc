#!/usr/bin/env bash
set -euo pipefail

BASE_COMMIT="f9c855f7cf04d603c9546bc01776c74806a879c1"
REPO="."
HEAD_COMMIT=""
OUTPUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO="$2"; shift 2;;
    --base)
      BASE_COMMIT="$2"; shift 2;;
    --head)
      HEAD_COMMIT="$2"; shift 2;;
    --output)
      OUTPUT="$2"; shift 2;;
    *)
      echo "Unknown arg: $1" >&2; exit 1;;
  esac
done

if [[ -z "$HEAD_COMMIT" ]]; then
  HEAD_COMMIT="$(git -C "$REPO" rev-parse HEAD)"
fi

if [[ -z "$OUTPUT" ]]; then
  OUTPUT="$(dirname "$0")/patches/gradloc.patch"
fi

mkdir -p "$(dirname "$OUTPUT")"

git -C "$REPO" diff "$BASE_COMMIT" "$HEAD_COMMIT" > "$OUTPUT"
sha256sum "$OUTPUT" > "$OUTPUT.sha256"
echo "Patch updated: $OUTPUT"
