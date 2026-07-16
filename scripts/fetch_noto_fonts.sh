#!/usr/bin/env bash
#
# fetch_noto_fonts.sh — download the Noto fonts that give job-seeker resumes
# glyph coverage for every writing system (v0.4: LTR, no tofu).
#
# Bundled families (OFL licensed, fetched from the notofonts GitHub mirror):
#   NotoSans-Regular.ttf          Latin + Cyrillic + Greek (covers the gaps the
#                                 TeX Gyre Termes main font has, e.g. GREEK
#                                 SMALL LETTER ETA WITH TONOS, U+03AE)
#   NotoSansArabic-Regular.ttf    Arabic
#   NotoSansHebrew-Regular.ttf    Hebrew
#   NotoSansDevanagari-Regular.ttf Devanagari (Hindi, Sanskrit, ...)
#
# These are copied into resume_template/fonts/Noto/ AND every LaTeX_Resume_<SCRIPT>/
# dir so the renderer finds them relative to the compiling .tex (no system install).
#
# Usage:  ./scripts/fetch_noto_fonts.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE="https://cdn.jsdelivr.net/gh/notofonts/notofonts.github.io@main/fonts"

# font file  ->  path under the notofonts mirror
FILES=(
  "NotoSans-Regular.ttf:NotoSans/hinted/ttf/NotoSans-Regular.ttf"
  "NotoSansArabic-Regular.ttf:NotoSansArabic/hinted/ttf/NotoSansArabic-Regular.ttf"
  "NotoSansHebrew-Regular.ttf:NotoSansHebrew/hinted/ttf/NotoSansHebrew-Regular.ttf"
  "NotoSansDevanagari-Regular.ttf:NotoSansDevanagari/hinted/ttf/NotoSansDevanagari-Regular.ttf"
)

echo "Fetching Noto fonts into $ROOT/resume_template/fonts/Noto/ ..."
mkdir -p "$ROOT/resume_template/fonts/Noto"
for entry in "${FILES[@]}"; do
  name="${entry%%:*}"
  url="$BASE/${entry#*:}"
  curl -sL --max-time 120 -o "$ROOT/resume_template/fonts/Noto/$name" "$url"
  printf '  %-32s %s bytes\n' "$name" "$(wc -c < "$ROOT/resume_template/fonts/Noto/$name")"
done

echo "Copying into every LaTeX_Resume_<SCRIPT>/fonts/Noto/ ..."
for d in "$ROOT"/LaTeX_Resume_*; do
  [ -d "$d" ] || continue
  mkdir -p "$d/fonts/Noto"
  cp -f "$ROOT/resume_template/fonts/Noto"/*.ttf "$d/fonts/Noto/"
  echo "  -> $d/fonts/Noto/"
done

echo "Done. Fonts are bundled; no system font install needed."
