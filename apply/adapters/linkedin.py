"""LinkedIn adapter.

LinkedIn's ToS prohibit automated scraping and form submission. This adapter:
  - inherits read_jd (public JD pages are partially readable without login,
    but full content requires auth — degrade gracefully),
  - sets tos_blocks_automation = True so the CLI never auto-fills/submits;
    it degrades to "open page + show prefill data".
"""
from .workday_generic import GenericAdapter


class LinkedInAdapter(GenericAdapter):
    name = "linkedin"
    tos_blocks_automation = True
