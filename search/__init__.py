# Aliases for root main.py: simplify imports of scraper functions.

from .sites.bpm_power import get_products as get_bpm_products
from .sites.esse_shop import get_products as get_esse_products

__all__ = ["get_bpm_products", "get_esse_products"]
