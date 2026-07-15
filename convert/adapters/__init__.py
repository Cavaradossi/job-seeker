"""Adapter registry for the convert pipeline."""
from .base import Adapter
from .markdown_to_latex import MarkdownToLatex
from .latex_to_pdf import LatexToPdf
from .latex_to_docx import LatexToDocx
from .docx_to_latex import DocxToLatex
from .markdown_to_pdf import MarkdownToPdf
from .markdown_to_docx import MarkdownToDocx
from .docx_to_markdown import DocxToMarkdown
from .docx_to_pdf import DocxToPdf
from .latex_to_markdown import LatexToMarkdown
from .pdf_to_markdown import PdfToMarkdown

__all__ = [
    "Adapter",
    "MarkdownToLatex",
    "LatexToPdf",
    "LatexToDocx",
    "DocxToLatex",
    "MarkdownToPdf",
    "MarkdownToDocx",
    "DocxToMarkdown",
    "DocxToPdf",
    "LatexToMarkdown",
    "PdfToMarkdown",
]
