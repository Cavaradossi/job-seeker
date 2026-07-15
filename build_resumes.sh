#!/usr/bin/env bash
#
# build_resumes.sh — cross-platform (macOS / Linux) build script for 申职器 (job-seeker).
# Behavior mirrors build_resumes.ps1 (Windows) and adds page-count reporting.
#
# Usage:
#   chmod +x ./build_resumes.sh
#   ./build_resumes.sh
#
# Requires: xelatex (MacTeX or TeX Live) + the LaTeX packages listed in docs/BUILD_MAC.md.
# Fonts are bundled in LaTeX_Resume_CN/fonts/ and LaTeX_Resume_EN/fonts/ — no system font install needed.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CN_DIR="$ROOT/LaTeX_Resume_CN"
EN_DIR="$ROOT/LaTeX_Resume_EN"
OUT_DIR="$ROOT/outputs"

# Compile list — must match build_resumes.ps1 exactly.
CN_FILES=(
  resume-zh_CN
  resume-zh_job
  resume-zh_backend_ops
  resume-zh_ai_eval
  resume-zh_jd_annichiman
  resume-zh_jd_bilaiwu
  resume-zh_jd_miaoda
  resume-zh_jd_bytedance
)

EN_FILES=(
  resume_job_en
  resume_backend_ops
  resume_ai_eval
  resume_web3
)

# PDF copy mapping: "source_pdf:destination_pdf" (relative to compile dir / outputs dir).
CN_MAP=(
  "resume-zh_CN.pdf:resume-zh_CN.pdf"
  "resume-zh_job.pdf:resume_job_cn.pdf"
  "resume-zh_backend_ops.pdf:resume_backend_ops_cn.pdf"
  "resume-zh_ai_eval.pdf:resume_ai_eval_cn.pdf"
  "resume-zh_jd_annichiman.pdf:resume_jd_annichiman_cn.pdf"
  "resume-zh_jd_bilaiwu.pdf:resume_jd_bilaiwu_cn.pdf"
  "resume-zh_jd_miaoda.pdf:resume_jd_miaoda_cn.pdf"
  "resume-zh_jd_bytedance.pdf:resume_jd_bytedance_cn.pdf"
)

EN_MAP=(
  "resume_job_en.pdf:resume_job_en.pdf"
  "resume_backend_ops.pdf:resume_backend_ops.pdf"
  "resume_ai_eval.pdf:resume_ai_eval.pdf"
  "resume_web3.pdf:resume_web3.pdf"
)

# Accumulate page-count reports: "file_basename: N page(s)".
declare -a PAGE_REPORT=()

check_xelatex() {
  if ! command -v xelatex >/dev/null 2>&1; then
    cat >&2 <<EOF
ERROR: xelatex not found on PATH.

Install a TeX distribution first:
  macOS:  brew install --cask mactex          # full, ~4 GB
          brew install --cask basictex        # minimal, then tlmgr install <pkgs>
  Linux:  sudo apt-get install -y texlive-full

See docs/BUILD_MAC.md for the full package list and the AdobeFangsongStd font fix.
EOF
    exit 2
  fi
}

# compile_one <dir> <tex_basename>
# Compiles <dir>/<tex_basename>.tex with xelatex; records page count; aborts on failure.
compile_one() {
  local dir="$1"
  local texbase="$2"
  local texfile="$texbase.tex"
  local logfile="$dir/$texbase.log"

  printf '  ==> xelatex %s\n' "$texfile"
  (
    cd "$dir"
    if ! xelatex -interaction=nonstopmode -halt-on-error "$texfile" >/dev/null 2>&1; then
      echo "FAILED: $texfile (see $logfile for details)" >&2
      if [[ -f "$logfile" ]]; then
        echo "----- last 50 lines of $logfile -----" >&2
        tail -n 50 "$logfile" >&2 || true
        echo "-------------------------------------" >&2
      fi
      exit 1
    fi
  )

  # Parse "Output written on FILE (N page)" or "(N pages)" from the xelatex log.
  local pages="?"
  if [[ -f "$logfile" ]]; then
    local line
    line=$(grep -oE 'Output written on [^ ]+ \([0-9]+ pages?\)' "$logfile" | head -n 1 || true)
    if [[ -n "$line" ]]; then
      pages=$(printf '%s' "$line" | grep -oE '[0-9]+ pages?' | grep -oE '[0-9]+' || echo "?")
    fi
  fi
  PAGE_REPORT+=("$texbase: $pages page(s)")
}

# copy_pdf <dir> <src_dst_pair>
# Copies <dir>/<src> to outputs/<dst>, overwriting.
copy_pdf() {
  local dir="$1"
  local pair="$2"
  local src="${pair%%:*}"
  local dst="${pair##*:}"
  cp -f "$dir/$src" "$OUT_DIR/$dst"
  printf '      -> outputs/%s\n' "$dst"
}

# cleanup_dir <dir>
# Removes *.aux *.log *.out *.pdf from the compile dir (PDFs already copied to outputs/).
cleanup_dir() {
  local dir="$1"
  rm -f "$dir"/*.aux "$dir"/*.log "$dir"/*.out "$dir"/*.pdf 2>/dev/null || true
}

main() {
  check_xelatex
  mkdir -p "$OUT_DIR"

  echo "=== Building Chinese resumes ($CN_DIR) ==="
  for f in "${CN_FILES[@]}"; do
    compile_one "$CN_DIR" "$f"
  done

  echo "=== Copying CN PDFs to outputs/ ==="
  for pair in "${CN_MAP[@]}"; do
    copy_pdf "$CN_DIR" "$pair"
  done

  echo "=== Building English resumes ($EN_DIR) ==="
  for f in "${EN_FILES[@]}"; do
    compile_one "$EN_DIR" "$f"
  done

  echo "=== Copying EN PDFs to outputs/ ==="
  for pair in "${EN_MAP[@]}"; do
    copy_pdf "$EN_DIR" "$pair"
  done

  echo "=== Cleaning up build artifacts ==="
  cleanup_dir "$CN_DIR"
  cleanup_dir "$EN_DIR"

  echo ""
  echo "Done. PDFs in outputs/"
  echo ""
  echo "Page counts:"
  for line in "${PAGE_REPORT[@]}"; do
    printf '  - %s\n' "$line"
  done
}

main "$@"
