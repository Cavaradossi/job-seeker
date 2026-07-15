#!/usr/bin/env bash
# Sync docs/skill/job-seeker/ → .codex/skills/, .cursor/skills/, and .workbuddy/skills/
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/docs/skill/job-seeker"
CODEX="$ROOT/.codex/skills/job-seeker"
CUR="$ROOT/.cursor/skills/job-seeker"
WB="$ROOT/.workbuddy/skills/job-seeker"

if [[ ! -f "$SRC/SKILL.md" ]]; then
  echo "ERROR: missing $SRC/SKILL.md" >&2
  exit 1
fi

mkdir -p "$CODEX/references" "$CODEX/agents" "$CUR/references" "$WB/references"

for f in SKILL.md SKILL.zh-CN.md checklist.md; do
  [[ -f "$SRC/$f" ]] || continue
  cp "$SRC/$f" "$CODEX/$f"
  cp "$SRC/$f" "$CUR/$f"
  cp "$SRC/$f" "$WB/$f"
done

python3 - "$CODEX/SKILL.md" <<'PY'
import re, sys
from pathlib import Path
p = Path(sys.argv[1])
text = p.read_text(encoding="utf-8")
text = re.sub(r"(?m)^(version|tags):.*\n", "", text)
p.write_text(text, encoding="utf-8")
PY

cp "$SRC/references/"* "$CODEX/references/"
cp "$SRC/references/"* "$CUR/references/"
cp "$SRC/references/"* "$WB/references/"
cp "$SRC/agents/openai.yaml" "$CODEX/agents/openai.yaml"

python3 - "$WB/SKILL.md" <<'PY'
import re, sys
from pathlib import Path
p = Path(sys.argv[1])
text = p.read_text(encoding="utf-8")
# Only modify the YAML frontmatter (first --- ... --- block). The SKILL body
# mentions "agent_created" in the editor-install table, so a whole-text check
# would always be True and silently skip the insertion (bug caught by CI).
m = re.match(r"^(---\n)(.*?\n)(---\n)", text, re.DOTALL)
if m and "agent_created:" not in m.group(2):
    text = text[:m.start(2)] + m.group(2) + "agent_created: true\n" + text[m.end(2):]
    p.write_text(text, encoding="utf-8")
PY

echo "Synced: $SRC -> $CODEX, $CUR, $WB"
