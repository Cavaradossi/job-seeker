# job-seeker — 申职器

> **Languages**: [English](README.md) · [简体中文](README.zh-CN.md)

**Tailor a clean LaTeX resume to any job description in minutes** — then convert it between Markdown / DOCX / PDF / LaTeX, and optionally prefill job applications behind a hard human-in-the-loop safety gate. Ships with bundled CJK fonts (compiles out of the box) and an Agent Skill that teaches your AI editor the whole workflow.

`MIT` · cross-platform (macOS · Linux · Windows) · LaTeX + pandoc + Playwright

---

## ✨ Why job-seeker?

Sending the same resume to every job gets you filtered out. Hand-tailoring one per JD is slow, keeping `.tex` / DOCX / Markdown in sync is painful, and submitting applications is error-prone. job-seeker turns that into one coherent flow:

- **Bring any format, get any format.** Start from `.tex`, `.md`, `.docx`, *or* `.pdf` — convert freely between all four without manual sync.
- **JD-aware variant picking.** Paste a JD, get a recommended resume variant.
- **Apply without losing control.** A browser assistant prefills forms but **never auto-submits** — every submission waits for your explicit `y`.
- **Honest resumes by design.** A built-in Skill enforces anti-inflation rules (no invented metrics, no inflated titles).

## 🚀 Features

- **Clean LaTeX template** with **bundled Adobe CJK fonts** — no system font install needed.
- **Cross-platform build scripts** (`build_resumes.sh` / `.ps1`) with page-count reporting.
- **Any-to-any format conversion** (`convert/`): LaTeX ↔ Markdown ↔ DOCX ↔ PDF — upload a resume in *any* of the four formats and convert to any other, via an adapter pattern with automatic BFS routing (PDF text is ingested with PyMuPDF).
- **JD → variant recommender** (`apply/`): rule-based keyword matching picks the right resume for the role.
- **Browser-assisted application** with site adapters (Boss直聘 / LinkedIn / generic ATS) and a **human-in-the-loop confirm gate**.
- **Application tracker** (CSV) + history audit log — every action recorded.
- **Agent Skill** (WorkBuddy / Cursor / editor-agnostic) that encodes the workflow and honesty boundaries.
- **CI** compiles the sample resume on every push/PR.

## 📦 Installation

**Prerequisites**

| Tool | Required for | Notes |
|------|--------------|-------|
| TeX Live (`xelatex`) | Compiling PDFs | macOS: `brew install --cask mactex` — full guide in [`docs/BUILD_MAC.md`](docs/BUILD_MAC.md) |
| Python 3.10+ | `convert/` and `apply/` | |
| pandoc | DOCX / Markdown conversion | PDF works with just `xelatex`; `brew install pandoc` |
| Playwright *(optional)* | Live browser prefill in `apply/` | `pip install playwright && playwright install chromium` |

**Setup**

```bash
git clone https://github.com/Cavaradossi/job-seeker.git
cd job-seeker
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## ⚡ Quick start

### 1. Compile the sample resume

```bash
cd resume_template
xelatex -interaction=nonstopmode sample-resume-en_US-zh_CN.tex
# → sample-resume-en_US-zh_CN.pdf (CJK fonts included, no extra setup)
```

### 2. Convert between formats

```bash
# The input format is inferred from the extension — start from ANY of .tex / .md / .docx / .pdf
python -m convert --input resume_template/sample-resume-en_US-zh_CN.tex --output outputs/sample.pdf
python -m convert --input resume_template/sample-resume-en_US-zh_CN.tex --output outputs/sample.docx
python -m convert --input my_resume.pdf   --output outputs/my_resume.md    # PDF → Markdown (text extracted with PyMuPDF)
python -m convert --input my_resume.docx  --output outputs/my_resume.tex   # DOCX → LaTeX
python -m convert --list-routes           # see every supported conversion
```

### 3. Tailor to a JD & rehearse the apply flow

```bash
python -m apply --jd-file apply/samples/sample_jd.html --dry-run    # read JD → recommend variant → render PDF
python -m apply --url https://example.com/jobs/123 --dry-run        # fetch a live JD from the web
python -m apply --jd-file apply/samples/sample_jd.html --rehearse   # feel the confirmation gate pause
```

## 💡 Usage examples

**Make a JD-specific variant.** Copy the general template, change only the headline, compile:

```bash
cp resume_template/sample-resume-en_US-zh_CN.tex LaTeX_Resume_CN/resume-zh_jd_acme.tex
# edit \centerline{...} headline to match the JD, then:
./build_resumes.sh
```

**Convert a Markdown draft to PDF** (uses pandoc's default template — not a resume layout, handy for drafts):

```bash
python -m convert --input notes.md --output notes.pdf
```

**Apply to a public ATS posting** (generic adapter; live prefill needs Playwright):

```bash
export JOB_SEEKER_NAME="Your Name"
export JOB_SEEKER_EMAIL="you@example.com"
python -m apply --url https://boards.greenhouse.io/acme/jobs/123 --variant resume_job_en
# → browser opens, fields prefilled, then it PAUSES for your [y/N] before submitting
```

## ⚙️ Configuration

- **Apply profile** — set via env vars (never stored in the repo):
  - `JOB_SEEKER_NAME`, `JOB_SEEKER_EMAIL`, `JOB_SEEKER_PHONE`
  - `JOB_SEEKER_CONFIRM=yes|no` — auto-answer the confirm gate (for scripting/tests only)
- **Resume variants** — drop your `.tex` files into `LaTeX_Resume_CN/` or `LaTeX_Resume_EN/`; the renderer searches those plus `resume_template/`.
- **Tool discovery** — `convert/tools.py` finds `pandoc` / `xelatex` / `latexmk` on `PATH` first, then falls back to common install locations (MacTeX, `~/texlive/*/bin/*`, Homebrew, `~/.local/bin`), so the CLI works even in non-interactive shells.
- **ToS-aware adapters** — Boss直聘 and LinkedIn set `tos_blocks_automation = True`, so `apply` degrades to "open page + show prefill data" instead of automating them.

## 📁 Project structure

```
job-seeker/
├── resume_template/        Clean LaTeX template + bundled CJK fonts + fontawesome
├── convert/                Phase 2: format conversion pipeline (MD/DOCX/PDF/LaTeX)
│   ├── adapters/           One adapter per conversion (pandoc / xelatex)
│   ├── pipeline.py         BFS routing + chained adapters
│   └── cli.py              python -m convert ...
├── apply/                  Phase 3: browser-assisted application
│   ├── adapters/           Site adapters (generic / boss_zhipin / linkedin)
│   ├── mapping/            JD→variant recommender + variant renderer
│   ├── confirm.py          Human-in-the-loop gate (submit() always blocks here)
│   ├── audit.py            Tracker CSV + history log
│   └── cli.py              python -m apply ...
├── docs/                    Build guide, open-source plan, tracker schema, example bank
├── docs/skill/job-seeker/  Portable Agent Skill (WorkBuddy / Cursor / generic)
├── build_resumes.sh/.ps1   Cross-platform build scripts
└── requirements.txt        Python deps for convert/ + apply/
```

## ❓ FAQ

**Do I need to install system fonts?**
No. The template bundles Adobe CJK fonts in `resume_template/fonts/`, so it compiles identically on any machine.

**Do I need pandoc?**
Only for DOCX / Markdown conversion. `tex → pdf` works with just `xelatex`.

**Will it auto-submit my job applications?**
**Never.** `submit()` always calls `confirm()` and blocks. Nothing is submitted without an explicit `y`. For Boss直聘 / LinkedIn (whose ToS prohibit automation), it doesn't even try — it opens the page and shows you the data to paste manually.

**Is my personal data safe in the public repo?**
Yes by design. `outputs/` (compiled PDFs + tracker CSV), `history/`, `docs/experience_bank.md`, and your real `.tex` variants are all gitignored. The public repo contains only the clean template + code, using `YOUR_NAME` / `your-email@example.com` placeholders.

**Which editors does the Skill support?**
WorkBuddy (auto-loads from `.workbuddy/skills/`), Cursor (copy `docs/skill/job-seeker/` to `.cursor/skills/`), or any editor — just open `docs/skill/job-seeker/SKILL.md` and follow it manually.

**Can I start from a PDF or Word doc instead of LaTeX?**
Yes. Upload any of `.tex` / `.md` / `.docx` / `.pdf` and convert to any other — the pipeline routes automatically. PDF is **text-only** on the way in (extracted with PyMuPDF): a scanned/image PDF has no text layer and will be rejected, and layout/styling is not recovered. Treat PDF-in as "recover the content, then re-typeset with the LaTeX template."

**The conversion to DOCX looks lossy — why?**
LaTeX ↔ DOCX is fundamentally lossy: custom resume macros (`\name`, `\centerline`, `\datedsubsection`, icons) don't survive. The DOCX is an editable text mirror, never a layout-accurate render. The `.tex → .pdf` path is the source of truth. (The CLI prints a `WARNING` on every lossy step.)

## 🤝 Contributing

Contributions are welcome — and there's plenty to do! A few good first areas:

- **New site adapter** for an ATS you use (Workday / Greenhouse / Lever variants welcome) — see `apply/adapters/workday_generic.py` as a template.
- **New conversion adapter** (e.g. HTML → PDF, or OCR for scanned PDFs) — implement the `Adapter` ABC in `convert/adapters/`.
- **More JD → variant rules** in `apply/mapping/jd_to_variant.py`.
- **Better field-detection heuristics** for the prefill step.

Before opening a PR:

1. Read the [open-source plan](docs/job_seeker_opensource_plan.md) for direction and the privacy strategy.
2. Respect the **honesty boundaries** in [`docs/skill/job-seeker/SKILL.md`](docs/skill/job-seeker/SKILL.md) §6 — no resume inflation, no invented metrics.
3. Add a test under `convert/tests/` or `apply/tests/` and run `pytest` (33 tests should stay green).
4. Use placeholders (`YOUR_NAME`, `your-email@example.com`) in any example content — never real personal data.

## 📄 License

MIT — see [`LICENSE`](LICENSE).

The `resume_template/` directory is derived from [billryan/resume](https://github.com/billryan/resume) (also MIT). All bundled fonts retain their original licenses.
