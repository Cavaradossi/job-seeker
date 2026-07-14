"""Adapter registry for the convert pipeline."""
from .base import Adapter
from .markdown_to_latex import MarkdownToLatex
from .latex_to_pdf import LatexToPdf
from .latex_to_docx import LatexToDocx
from .docx_to_latex import DocxToLatex
from .markdown_to_pdf import MarkdownToPdf

__all__ = [
    "Adapter",
    "MarkdownToLatex",
    "LatexToPdf",
    "LatexToDocx",
    "DocxToLatex",
    "MarkdownToPdf",
]
