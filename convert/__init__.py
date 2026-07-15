"""job-seeker format conversion pipeline (Phase 2).

Single source document -> multiple output formats
(Markdown <-> DOCX <-> PDF <-> LaTeX). Each adapter does one conversion;
Pipeline chains them with temp intermediates.

    python -m convert --input resume_template/sample-resume-en_US-zh_CN.tex --output sample.pdf
    python -m convert --list-routes
"""
from .adapters.base import Adapter
from .pipeline import Pipeline, route

__all__ = ["Pipeline", "route", "Adapter"]
__version__ = "0.1.0"
