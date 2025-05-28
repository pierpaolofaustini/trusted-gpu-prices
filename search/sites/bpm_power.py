from search.core import scrape_site

BPM_CONFIG = {
    "search_url_tpl": "https://www.bpm-power.com/it/ricerca?k={terms}",
    "pagination": {
        "type": "param",
        "param_name": "page"
    },
    "selectors": {
        "card": "#divGridProducts .bordoCat",
        "name": "h4.nomeprod_category",
        "price": "p.prezzoCat",
        "sold_out": "span.dispoNo",
        "pagination": "ul.pagination li.page-item",
    }
}

def get_products(brand=None, model=None):
    return scrape_site(brand, model, BPM_CONFIG)




