"""Boss直聘 adapter.

Boss直聘 requires login to view full JDs and its ToS prohibit automated
access/scraping. This adapter therefore:
  - inherits read_jd (may hit a login wall — degrade gracefully),
  - sets tos_blocks_automation = True so the CLI never attempts automated
    prefill/submit; it degrades to "open page + show prefill data".
"""
from .workday_generic import GenericAdapter


class BossZhipinAdapter(GenericAdapter):
    name = "boss_zhipin"
    tos_blocks_automation = True
