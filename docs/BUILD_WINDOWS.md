# Building resumes on Windows

Install the TeX toolchain on Windows and compile resumes with PowerShell.
For macOS/Linux, see [`BUILD_MAC.md`](BUILD_MAC.md).

---

## 1. Install MiKTeX (recommended)

1. Download **MiKTeX** from [https://miktex.org/download](https://miktex.org/download)
2. Run the installer (64-bit). Enable **Install missing packages on-the-fly** when prompted.
3. Open a **new** PowerShell window and verify:

```powershell
xelatex --version
```

Typical install path (added to PATH automatically):

`C:\Users\<YOU>\AppData\Local\Programs\MiKTeX\miktex\bin\x64\`

`build_resumes.ps1` also checks common MiKTeX and TeX Live install locations if
PATH is incomplete, then temporarily prepends the discovered TeX bin directory
for that build process.

### Optional: TeX Live on Windows

TeX Live also works. After install, ensure `xelatex` is on PATH. The `convert`
module searches MiKTeX and TeX Live locations if PATH is incomplete.

---

## 2. Python environment

From the repo root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If script execution is blocked:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

---

## 3. Optional tools

| Tool | Purpose | Install |
|------|---------|---------|
| **pandoc** | DOCX / Markdown conversion | [pandoc.org/installing](https://pandoc.org/installing.html) or `winget install JohnMacFarlane.Pandoc` |
| **Perl** | Only if you want `latexmk` | Strawberry Perl — **not required**; job-seeker prefers `xelatex` on Windows |
| **Playwright** | Live browser prefill in `apply/` | `pip install playwright` then `playwright install chromium` |

> **Note:** MiKTeX ships `latexmk` but it often needs Perl. The `convert` pipeline
> uses **`xelatex` directly on Windows** so you do not need Perl for PDF builds.

---

## 4. First compile (sample template)

No private `LaTeX_Resume_*` folder required:

```powershell
cd resume_template
xelatex -interaction=nonstopmode sample-resume-en_US-zh_CN.tex
# -> sample-resume-en_US-zh_CN.pdf (bundled CJK fonts, no extra font install)
```

Or via the convert CLI:

```powershell
python -m convert --input resume_template/sample-resume-en_US-zh_CN.tex --output outputs/sample.pdf
```

---

## 5. Build all private variants

Copy and personalize templates first:

```powershell
Copy-Item -Recurse resume_template\*.tex,resume_template\*.cls,resume_template\*.sty LaTeX_Resume_CN\
# edit .tex files, then from repo root:
.\build_resumes.ps1
```

The script expects `LaTeX_Resume_CN/` and `LaTeX_Resume_EN/` with the filenames
listed in `build_resumes.ps1` (same mapping as `build_resumes.sh`).

---

## 6. Environment variables (`apply/`)

PowerShell syntax (not `export`):

```powershell
$env:JOB_SEEKER_NAME = "Your Name"
$env:JOB_SEEKER_EMAIL = "you@example.com"
python -m apply --jd-file apply\samples\sample_jd.html --dry-run
```

---

## 7. Cursor on Windows

- Open the repo in Cursor — Skill loads from `.cursor\skills\job-seeker\`
- Resume rules apply when editing `*.tex` under `resume_template/` or `LaTeX_Resume_*`
- See [`skill/CURSOR.md`](skill/CURSOR.md) and root [`AGENTS.md`](../AGENTS.md)

Sync skill mirrors after editing `docs/skill/job-seeker/`:

```powershell
.\scripts\sync_skills.ps1
```

---

## 8. Common errors

### `latexmk` / Perl not found

Ignore if you use `build_resumes.ps1` or `python -m convert` — they call
`xelatex` on Windows. Install Perl only if you explicitly want `latexmk`.

### `! LaTeX Error: File 'xxx.sty' not found`

Open **MiKTeX Console** → Updates → install missing packages, or run once in
PowerShell (MiKTeX will prompt to install):

```powershell
xelatex -interaction=nonstopmode resume_template\sample-resume-en_US-zh_CN.tex
```

### `xelatex` not recognized

Restart the terminal after MiKTeX install, or add the `miktex\bin\x64` folder to
your user PATH in Windows Settings.

### `Unicode-math` / pandoc PDF errors

When converting Markdown → PDF via pandoc, install missing MiKTeX packages
(`unicode-math`, etc.) or compile from `.tex` instead (layout source of truth).

### PowerShell cannot run `build_resumes.ps1`

```powershell
powershell -ExecutionPolicy Bypass -File .\build_resumes.ps1
```

### Path separators in docs

Use `\` or `/` in PowerShell for local paths. In Skill/docs for agents, prefer
forward slashes (`resume_template/sample.tex`) — they work on Windows too.

### Garbled dashes/arrows in `convert` / `apply` console output

`cli.py` output uses em dashes (`—`) and arrows for readability. On a default
Windows console (codepage 936/GBK, common on zh-CN Windows), these can print
as `??` or mojibake — this is a console rendering issue, not a bug in the
output. Fix for the session:

```powershell
chcp 65001            # switch the console to UTF-8
$env:PYTHONUTF8 = "1" # or force Python's UTF-8 mode
```

Resume PDFs themselves are unaffected — this only affects terminal text.

---

## 9. Run tests (no full TeX required)

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest convert/tests apply/tests -q -k "not real"
```

Tests ending in `_real` need a working `xelatex` + optional pandoc.
