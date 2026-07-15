#!/usr/bin/env bash
# Sync docs/skill/job-seeker/ → .cursor/skills/ and .workbuddy/skills/
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/docs/skill/job-seeker"
CUR="$ROOT/.cursor/skills/job-seeker"
WB="$ROOT/.workbuddy/skills/job-seeker"

if [[ ! -f "$SRC/SKILL.md" ]]; then
  echo "ERROR: missing $SRC/SKILL.md" >&2
  exit 1
fi

mkdir -p "$CUR/references" "$WB/references"

for f in SKILL.md SKILL.zh-CN.md checklist.md; do
  [[ -f "$SRC/$f" ]] || continue
  cp "$SRC/$f" "$CUR/$f"
  cp "$SRC/$f" "$WB/$f"
done

cp "$SRC/references/"* "$CUR/references/"
cp "$SRC/references/"* "$WB/references/"

python3 - "$WB/SKILL.md" <<'PY'
import re, sys
from pathlib import Path
p = Path(sys.argv[1])
text = p.read_text(encoding="utf-8")
if "agent_created:" not in text and text.startswith("---"):
    text = re.sub(
        r"(^---\n(?:.*\n)*?)(---\n)",
        r"\1agent_created: true\n\2",
        text,
        count=1,
    )
    p.write_text(text, encoding="utf-8")
PY

echo "Synced: $SRC -> $CUR, $WB"
