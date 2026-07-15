# LaTeX Resume Template

A clean, self-contained bilingual (English / 简体中文) résumé template compiled with **XeLaTeX**. All Adobe CJK fonts and the FontAwesome icon set are bundled, so it renders identically on any machine with no system font installation.

## Contents

| File | Purpose |
|------|---------|
| `sample-resume-en_US-zh_CN.tex` | Sample résumé source (placeholders — replace with your own content) |
| `resume.cls` | Document class defining the layout and helper macros |
| `fonts/` | Bundled Adobe CJK fonts (Song / Kai / Hei / FangSong) |
| `fontawesomesymbols-*.tex` | FontAwesome glyph definitions |

## Usage

```bash
# Compile from inside this directory (so resume.cls + fonts resolve):
cd resume_template
xelatex -interaction=nonstopmode sample-resume-en_US-zh_CN.tex
# → sample-resume-en_US-zh_CN.pdf
```

Or use the format-conversion pipeline from the repo root:

```bash
python -m convert --input resume_template/sample-resume-en_US-zh_CN.tex --output outputs/sample.pdf
```

The sample uses `YOUR_NAME` / `your-email@example.com` / `your-org` placeholders — edit the `.tex` to fill in your real details.

## Acknowledgments

This template is derived from [billryan/resume](https://github.com/billryan/resume) (MIT). Bundled fonts retain their original licenses.
