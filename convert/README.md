# convert/ — format conversion pipeline (Phase 2)

Single source document → multiple output formats (Markdown ↔ DOCX ↔ PDF ↔ LaTeX).
Each adapter does one conversion; `Pipeline` chains them with temp intermediates.

## Layout

```
convert/
├── tools.py                      # locate pandoc / xelatex / latexmk across platforms
├── adapters/
│   ├── base.py                   # Adapter ABC: convert(input, output) -> bool
│   ├── markdown_to_latex.py      # pandoc
│   ├── latex_to_pdf.py           # latexmk (preferred) / xelatex
│   ├── latex_to_docx.py          # pandoc  (LOSSY)
│   ├── docx_to_latex.py          # pandoc  (LOSSY)
│   └── markdown_to_pdf.py        # pandoc --pdf-engine=xelatex
├── pipeline.py                   # BFS route by extension + Pipeline chain
├── cli.py                        # python -m convert ...
└── tests/test_pipeline.py
```

## Usage

```bash
# Activate the venv first
source .venv/bin/activate

# Auto-route by extension (prints the chosen chain + lossy warnings)
python -m convert --input resume_template/HouJP-en_US-zh_CN.tex --output sample.pdf
python -m convert --input resume_template/HouJP-en_US-zh_CN.tex --output sample.docx
python -m convert --input notes.md --output notes.pdf

# List supported edges
python -m convert --list-routes

# Tests
pytest convert/tests/
```

## Supported routes

| From | To   | Adapter            | Lossy? |
|------|------|--------------------|--------|
| md   | tex  | MarkdownToLatex    | no (standard MD) |
| tex  | pdf  | LatexToPdf         | no |
| tex  | docx | LatexToDocx        | **yes** — custom resume macros dropped |
| docx | tex  | DocxToLatex        | **yes** — generic article-class output |
| md   | pdf  | MarkdownToPdf      | uses pandoc default template (not a resume layout) |

Multi-hop routes are resolved automatically, e.g. `md → docx` runs
`MarkdownToLatex` then `LatexToDocx`.

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
