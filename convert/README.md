# convert/ — format conversion pipeline (Phase 2)

Convert a résumé between **any** of four formats — **Markdown ↔ DOCX ↔ PDF ↔ LaTeX** —
in any direction. Upload your existing resume in whichever format you have
(including a PDF) and export it to any of the others. Each adapter does one
conversion; `Pipeline` auto-routes and chains them with temp intermediates.

## Layout

```
convert/
├── tools.py                      # locate pandoc / xelatex / latexmk across platforms
├── adapters/
│   ├── base.py                   # Adapter ABC: convert(input, output) -> bool
│   ├── markdown_to_latex.py      # pandoc
│   ├── markdown_to_docx.py       # pandoc
│   ├── markdown_to_pdf.py        # pandoc --pdf-engine=xelatex
│   ├── latex_to_pdf.py           # latexmk (preferred) / xelatex
│   ├── latex_to_docx.py          # pandoc  (LOSSY)
│   ├── latex_to_markdown.py      # pandoc  (LOSSY)
│   ├── docx_to_latex.py          # pandoc  (LOSSY)
│   ├── docx_to_markdown.py       # pandoc  (LOSSY)
│   ├── docx_to_pdf.py            # pandoc --pdf-engine=xelatex (LOSSY layout)
│   └── pdf_to_markdown.py        # PyMuPDF text extraction (LOSSY — PDF input)
├── pipeline.py                   # BFS route by extension + Pipeline chain
├── cli.py                        # python -m convert ...
└── tests/test_pipeline.py
```

## Usage

```bash
# Activate the venv first
source .venv/bin/activate

# Auto-route by extension (prints the chosen chain + lossy warnings)
python -m convert --input resume_template/sample-resume-en_US-zh_CN.tex --output sample.pdf
python -m convert --input resume_template/sample-resume-en_US-zh_CN.tex --output sample.docx
python -m convert --input my-resume.pdf  --output my-resume.md     # PDF as INPUT
python -m convert --input my-resume.docx --output my-resume.pdf
python -m convert --input notes.md       --output notes.pdf

# List supported edges
python -m convert --list-routes

# Tests
pytest convert/tests/
```

## Any-to-any conversion matrix

Rows = source, columns = target. `·` = same format (copied). Every cell is
reachable; multi-hop routes are resolved automatically.

| from → to | **md** | **tex** | **docx** | **pdf** |
|-----------|--------|---------|----------|---------|
| **md**    | ·      | direct  | direct   | direct  |
| **tex**   | direct (lossy) | · | direct (lossy) | direct |
| **docx**  | direct (lossy) | direct (lossy) | · | direct (lossy) |
| **pdf**   | direct (lossy) | via md (lossy) | via md (lossy) | · |

### Direct adapter edges

| From | To   | Adapter          | Tool    | Lossy? |
|------|------|------------------|---------|--------|
| md   | tex  | MarkdownToLatex  | pandoc  | no (standard MD) |
| md   | docx | MarkdownToDocx   | pandoc  | no (standard MD) |
| md   | pdf  | MarkdownToPdf    | pandoc + xelatex | pandoc default template (not a resume layout) |
| tex  | pdf  | LatexToPdf       | latexmk / xelatex | no |
| tex  | docx | LatexToDocx      | pandoc  | **yes** — custom resume macros dropped |
| tex  | md   | LatexToMarkdown  | pandoc  | **yes** — macros + layout dropped |
| docx | tex  | DocxToLatex      | pandoc  | **yes** — generic article-class output |
| docx | md   | DocxToMarkdown   | pandoc  | **yes** — Word styling dropped |
| docx | pdf  | DocxToPdf        | pandoc + xelatex | **yes** — re-typeset, not Word-accurate |
| pdf  | md   | PdfToMarkdown    | PyMuPDF | **yes** — text-only extraction |

### PDF as input (important caveats)

pandoc cannot read PDF, so PDF ingestion uses **PyMuPDF** (`pip install pymupdf`)
to extract the text layer. A PDF stores glyphs and positions, not semantic
structure — so **headings, columns, tables, bullets, fonts, and icons are not
reliably recovered**. You get readable text in reading order; review and
re-structure the Markdown before converting onward. Scanned / image-only PDFs
have no text layer and are not supported (OCR is out of scope).

`pdf → tex` and `pdf → docx` run automatically as `pdf → md → {tex,docx}`.

## Design rules (honoured)

- Each adapter does **one** thing: `convert(input_path, output_path) -> bool`.
- `Pipeline(MdToLatex(), LatexToPdf()).run("in.md", "out.pdf")` chains them.
- LaTeX ↔ DOCX is **not** lossless — lossy steps print a WARNING and are
  documented in each adapter's `lossy_note`.
- The `.tex` is the source of truth for PDF; Markdown is for editing
  convenience. Converters **never** auto-rewrite a curated `.tex`.
- `LatexToPdf` compiles in the `.tex`'s directory so local `.cls` / `.sty`
  and bundled fonts are found (matches `build_resumes.sh`). Build artifacts
  (`.aux`/`.log`/`.out`) are cleaned up; the source dir is otherwise untouched.

## Tool discovery

`convert/tools.py` finds `pandoc` / `xelatex` / `latexmk` on `PATH` first,
then falls back to common TeX install locations (MacTeX `/Library/TeX/texbin`,
user-level `~/texlive/*/bin/*`, system `/usr/local/texlive/*/bin/*`). TeX bin
dirs are prepended to `PATH` for subprocess calls so xelatex finds its support
tools (`kpsewhich`, `mktexmf`, ...). This makes the CLI work in non-interactive
shells that don't source `~/.zshrc`/`~/.bashrc`.
