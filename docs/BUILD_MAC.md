# Building resumes on macOS

This document explains how to install the TeX toolchain on macOS and compile the resumes in this repo with `./build_resumes.sh`.

The same general flow applies to Linux (`sudo apt-get install -y texlive-full` instead of MacTeX).

---

## 1. Install a TeX distribution

You need `xelatex` plus a set of LaTeX packages. Two options:

### Option A — MacTeX (recommended, ~4 GB)

Installs everything; no manual package installs needed.

```bash
brew install --cask mactex
# After install, reload your shell so /Library/TeX/texbin is on PATH:
eval "$(/usr/libexec/path_helper)"
xelatex --version   # sanity check
```

### Option B — BasicTeX (~100 MB, more manual work)

Smaller download, but you must install the required packages yourself with `tlmgr`:

```bash
brew install --cask basictex
eval "$(/usr/libexec/path_helper)"

sudo tlmgr update --self
sudo tlmgr install \
  xltxtra xifthen fontspec hyperref url geometry titlesec enumitem nth \
  progressbar xecjk setspace calc ifxetex ifluatex \
  realscripts ifmtarg

xelatex --version
```

If you hit "package not found" errors during compile, install the missing package with `sudo tlmgr install <name>` and retry. MacTeX (Option A) avoids this entirely.

> **Note on `realscripts` and `ifmtarg`**: these are dependencies of `xltxtra` and `xifthen` respectively. Some TeX Live collections don't auto-install them; the `tlmgr install` line above includes them explicitly to avoid `File 'realscripts.sty' not found` and `File 'ifmtarg.sty' not found` errors.

### Option C — User-level TeX Live (no sudo required)

If you don't have admin rights (e.g. on a managed Mac), install TeX Live to a user-writable directory with `install-tl`:

```bash
# 1. Download the installer
cd /tmp
curl -L -O https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz
tar xzf install-tl-unx.tar.gz
cd install-tl-2*/

# 2. Create a profile (adjust TEXDIR to your home)
cat > /tmp/texlive.profile <<'EOF'
selected_scheme scheme-small
TEXDIR /Users/YOUR_USERNAME/texlive/2025
TEXMFCONFIG /Users/YOUR_USERNAME/.texlive2025/texmf-config
TEXMFHOME /Users/YOUR_USERNAME/texmf
TEXMFLOCAL /Users/YOUR_USERNAME/texlive/texmf-local
TEXMFSYSCONFIG /Users/YOUR_USERNAME/texlive/2025/texmf-config
TEXMFSYSVAR /Users/YOUR_USERNAME/texlive/2025/texmf-var
option_doc 0
option_src 0
option_adjustrepo 0
option_desktop_integration 0
option_file_assocs 0
option_path 0
option_post_code 1
option_sys_bin /Users/YOUR_USERNAME/texlive/2025/bin
EOF

# 3. Run the installer (point at a fast mirror if CTAN is slow)
perl install-tl --profile=/tmp/texlive.profile --no-interaction \
  --repository https://mirrors.ustc.edu.cn/CTAN/systems/texlive/tlnet/

# 4. Add to PATH (add this to ~/.zshrc or ~/.bashrc for persistence)
export PATH="$HOME/texlive/2025/bin/universal-darwin:$PATH"

# 5. Install the extra packages the resumes need
tlmgr option repository https://mirrors.ustc.edu.cn/CTAN/systems/texlive/tlnet/
tlmgr install \
  xltxtra xifthen fontspec hyperref url geometry titlesec enumitem nth \
  progressbar xecjk setspace calc ifxetex ifluatex \
  realscripts ifmtarg

xelatex --version
```

`scheme-small` includes LaTeX + xelatex + common packages (fontspec, hyperref, geometry, enumitem). The `tlmgr install` line adds the remaining packages the resumes need (`xecjk` for Chinese, `progressbar` for the progress-bar command, etc.).

Use a nearby CTAN mirror for faster downloads:
- China: `https://mirrors.ustc.edu.cn/CTAN/systems/texlive/tlnet/`
- China: `https://mirrors.tuna.tsinghua.edu.cn/CTAN/systems/texlive/tlnet/`
- Global: `https://mirror.ctan.org/systems/texlive/tlnet/`

---

## 2. Verify the Adobe CJK fonts are in place

The Chinese resumes (`LaTeX_Resume_CN/*.tex`) load `zh_CN-Adobefonts_external.sty`, which sets:

```latex
\setCJKmainfont{AdobeSongStd-Light.otf}
\setCJKsansfont{AdobeHeitiStd-Regular.otf}
\setCJKmonofont{AdobeFangsongStd-Regular.otf}   % <- this one was missing historically
```

All four Adobe OTF files must exist in `LaTeX_Resume_CN/fonts/zh_CN-Adobe/`:

```bash
ls LaTeX_Resume_CN/fonts/zh_CN-Adobe/
# Expected:
#   AdobeFangsongStd-Regular.otf
#   AdobeHeitiStd-Regular.otf
#   AdobeKaitiStd-Regular.otf
#   AdobeSongStd-Light.otf
```

If any are missing, copy them from `resume_template/fonts/zh_CN-Adobe/` (the LaTeX template ships all four):

```bash
cp resume_template/fonts/zh_CN-Adobe/*.otf LaTeX_Resume_CN/fonts/zh_CN-Adobe/
```

The English resumes (`LaTeX_Resume_EN/*.tex`) do **not** use CJK fonts — they only need the Latin fonts in `fonts/Main/` and `fonts/fontawesome/opentype/`, which are already bundled.

---

## 3. Build

From the repo root:

```bash
chmod +x ./build_resumes.sh
./build_resumes.sh
```

The script:

1. Compiles each `.tex` file with `xelatex -interaction=nonstopmode -halt-on-error`
2. Copies the resulting PDFs to `outputs/` (with the rename mapping defined in the script)
3. Cleans up `*.aux`, `*.log`, `*.out`, `*.pdf` from `LaTeX_Resume_CN/` and `LaTeX_Resume_EN/`
4. Prints a page-count summary parsed from the xelatex logs

On success, you should see all 12 PDFs in `outputs/` and a table like:

```
Page counts:
  - resume-zh_CN: 2 page(s)
  - resume-zh_job: 1 page(s)
  ...
```

---

## 4. Page-count expectations

| File | Expected pages |
|------|----------------|
| `resume-zh_CN.pdf` | multi-page (full version with research) |
| `resume_job_cn.pdf` | 1 page |
| `resume_backend_ops_cn.pdf` | 1 page |
| `resume_ai_eval_cn.pdf` | 1 page |
| `resume_jd_*_cn.pdf` | 1 page each (4 JD-specific variants) |
| `resume_job_en.pdf` | **1 page** (acceptance criterion) |
| `resume_backend_ops.pdf` | 1 page |
| `resume_ai_eval.pdf` | 1 page |
| `resume_web3.pdf` | 1 page |

If `resume_job_en.pdf` is more than 1 page, the bullets need tightening — see `docs/work_buddy_master_prompt.md` §6.4.

---

## 5. Common errors

### `! LaTeX Error: File 'xecjk.sty' not found.`
Install the missing package: `sudo tlmgr install xecjk` (BasicTeX only — MacTeX ships it).

### `! fontspec error: cannot find font "AdobeFangsongStd-Regular.otf"`
The Adobe OTF is missing from `LaTeX_Resume_CN/fonts/zh_CN-Adobe/`. See §2 above.

### `xelatex: command not found`
The TeX bin directory is not on your PATH. Run `eval "$(/usr/libexec/path_helper)"`, or open a new terminal tab.

### Compile succeeds but PDF looks wrong (missing icons)
The `fontawesome.sty` requires `FontAwesome.otf` in `fonts/fontawesome/opentype/`. Both `LaTeX_Resume_CN/` and `LaTeX_Resume_EN/` ship it; check it wasn't accidentally deleted by an over-aggressive cleanup.

### `./build_resumes.sh: permission denied`
Run `chmod +x ./build_resumes.sh` once.

---

## 6. CI (GitHub Actions)

The repo includes `.github/workflows/build-resumes.yml` which compiles all resumes on push/PR to `main` using the `ghcr.io/xu-cheng/texlive-full:latest` Docker image. See the workflow file for details.
