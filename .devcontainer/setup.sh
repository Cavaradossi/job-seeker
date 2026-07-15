#!/usr/bin/env bash
# Codespaces / devcontainer first-run setup.
# Installs TinyTeX (minimal XeLaTeX) + the exact LaTeX packages the resume
# template needs, then the Python deps, then smoke-compiles the sample resume.
# Idempotent: safe to re-run on rebuild.
set -euo pipefail

echo "[setup] 1/4  TinyTeX (minimal XeLaTeX)..."
if ! command -v xelatex >/dev/null 2>&1; then
  wget -qO- "https://yihui.org/tinytex/install-bin-unix.sh" | sh
fi

# Expose TinyTeX binaries on PATH regardless of CPU arch (x86_64 / aarch64).
TEXBIN="$(echo "$HOME/.TinyTeX/bin/"*)"
if [ -n "$TEXBIN" ] && [ -d "$TEXBIN" ]; then
  ln -sfn "$TEXBIN" "$HOME/.tinytex-bin"          # stable path for remoteEnv
  "$TEXBIN/tlmgr" path add 2>/dev/null || true
  case ":$PATH:" in
    *":$TEXBIN:"*) ;;
    *) echo "export PATH=\"$TEXBIN:\$PATH\"" >> "$HOME/.bashrc" ;;
  esac
  export PATH="$TEXBIN:$PATH"
fi

echo "[setup] 2/4  LaTeX packages the template needs..."
# xeCJK + fontspec (CJK via bundled Adobe fonts), plus the resume.cls deps.
tlmgr install \
    xecjk fontspec xltxtra xifthen titlesec enumitem nth \
    cite setspace calc ifxetex ifluatex hyperref xcolor \
    polyglossia fancyhdr tabularx multicol ctex \
    2>/dev/null || true

echo "[setup] 3/4  Python deps (requirements.txt)..."
pip install -r requirements.txt 2>/dev/null \
  || pip install --user -r requirements.txt

echo "[setup] 4/4  smoke-compile the sample resume..."
if xelatex -interaction=nonstopmode -halt-on-error \
     -output-directory resume_template \
     resume_template/sample-resume-en_US-zh_CN.tex >/dev/null 2>&1; then
  echo "[setup] sample PDF built OK"
else
  echo "[setup] WARNING: sample compile failed — see resume_template/*.log"
fi

echo "[setup] done. Try:  make build   |   python -m convert --fidelity-matrix"
