import urllib.parse
from search.core import scrape_site

ESSE_CONFIG = {
    "search_url_tpl": (
        "https://www.esseshop.it/?s={terms}"
        "&feat[Categoria][0]={cat}"
    ),
    "extra": {
        "cat": urllib.parse.quote("Schede video ")
    },
    "pagination": {
        "type": "param",
        "param_name": "page"
    },
    "selectors": {
        "card": "#sniperfast_results_wrapper div.sniperfast_product",
        "name":  "div.sniperfast_prod_name", 
        "price": "div.sniperfast_prod_price",
        "sold_out": "span.label.label-arriving",
        "pagination": "a.next_page"
    }
}

def get_products(brand=None, model=None):
    return scrape_site(brand, model, ESSE_CONFIG)








