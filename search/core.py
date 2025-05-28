import time
import re
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    StaleElementReferenceException,
    NoSuchElementException,
    TimeoutException
)

# Using type hints for better readability and static analysis.
def parse_price(price_str: str) -> float:
    """
    Transform (example):
     - '1.234,56 €' to 1234.56
     - '330.66 €' to 330.66
     - '284,59 €' to 284.59
    """
    s = price_str.replace("€", "").strip()
    if "," in s:
        # If comma present, strip thousand separators and convert comma to decimal point.
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(" ", "")
    # Extracting numeric part + decimal, otherwise following float could return ValueError.
    m = re.search(r"\d+(\.\d+)?", s)
    return float(m.group(0)) if m else float("inf")

"""
    Remove all non-alphanumeric characters and lowercase.
    E.g. "RX 6600  Ti" → "rx6600ti"
"""
def normalize(s: str) -> str:    
    return re.sub(r'[^0-9a-z]', '', s.lower())

# Initialize Chrome driver.
def init_driver():
    opts = Options()
    opts.add_argument("--headless") # Headless Chrome to speed up scraping.
    opts.add_argument("--disable-gpu") # Disable GPU for stability.
    return webdriver.Chrome(service=Service(), options=opts)

"""
    Always build a search URL based on model (and optional brand).
    Pagination via param if configured.
"""
def build_url(brand, model, config, page=None):
    """
    Creates list [brand, model]. Filtering by None, eliminates Falsy (e.g. "" if no brand input).
    Then, uses "+" operator to combine brand and model (e.g. MSI, 4060 = MSI+4060).
    If no brand is present, it gets only 4060. 
    """
    raw_terms = "+".join(filter(None, [brand, model]))

    """
    Use urllib.parse.quote_plus to URL-encode the search terms:
      • encode '+' as '%2B'
      • convert spaces to '+'
      • handle special/non-ASCII characters (e.g. 'é' → '%C3%A9')
    Example (msi+4060):
      https://www.bpm-power.com/it/ricerca?k=msi%2B4060
    Follows URL standard for query string encoding.
    """
    terms = urllib.parse.quote_plus(raw_terms)

    url = config["search_url_tpl"].format(
        terms=terms,
        **config.get("extra", {})
    )

    # Pagination if needed.
    pag = config.get("pagination", {})
    if pag.get("type") == "param" and page is not None:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}{pag['param_name']}={page}"
    return url

"""
    Generic scraper driven by config. Returns list of dict:
      - name
      - price        (string)
      - price_value  (float)
      - availability
"""
def scrape_site(brand=None, model=None, config=None):
    # RAW INPUT: lowercase + strip only (before and after), preserve spaces in the middle.
    # Used to build the search query URL with original terms intact.
    brand_n = brand.lower().strip() if brand else None
    model_n = model.lower().strip() 

    # NORMALIZATION: remove all non-alphanumeric characters (no spaces).
    # Used for robust matching of model/brand against the scraped product names.
    brand_norm = normalize(brand_n) if brand_n else None
    model_norm = normalize(model_n) 

    driver = init_driver()
    products = []
    page = 1

    try:
        while True:
            url = build_url(brand_n, model_n, config, page)
            driver.get(url)

            # Wait up to 15s for at least one product card to load.
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, config["selectors"]["card"]))
            )

            cards = driver.find_elements(By.CSS_SELECTOR, config["selectors"]["card"])

            # Iterate by index to avoid stale references.
            for idx in range(len(cards)):

                # Up to 3 retries for each card if stall.
                retries = 3
                while retries:
                    try:
                        card = driver.find_elements(By.CSS_SELECTOR, config["selectors"]["card"])[idx]

                        # Skip sold-out/Arriving products.
                        if config["selectors"].get("sold_out") and \
                           card.find_elements(By.CSS_SELECTOR, config["selectors"]["sold_out"]):
                            break

                        # Extract and normalize name.
                        name = "—"
                        sel_name = config["selectors"]["name"]

                        if sel_name:
                            try:
                                name = card.find_element(By.CSS_SELECTOR, sel_name).text.strip()
                            except NoSuchElementException:
                                pass
                        name_norm = normalize(name) 

                        # Check if card is present, if not, go the next one.
                        if brand_norm and brand_norm not in name_norm:
                            break
                        if model_norm not in name_norm:
                            break

                        # Extract price.
                        sel_price = config["selectors"].get("price")
                        price = "Not available"

                        try:
                            price = card.find_element(By.CSS_SELECTOR, sel_price).text.strip()
                        except Exception:
                            pass

                        products.append({
                            "name": name,
                            "price": price,
                            "price_value": parse_price(price)
                        })

                        # Live-update the product count on the same console line by using carriage return, no newline, and immediate flush.
                        print(f"\r🔍 Prodotti trovati: {len(products)}", end="", flush=True)
                        break

                    # If the element becomes stale, retry 2 other times with a short pause; for any other error, avoid this card.
                    except StaleElementReferenceException:
                        retries -= 1
                        time.sleep(0.2)
                    except Exception:
                        break

            # Pagination: start at page=1 and keep incrementing the 'page' parameter (page=1,2,3,…) until the pagination_test selector is absent, then stop.
            pag = config.get("pagination", {})
            # Pagination type is by param (e.g. ?page=1, ?page=2, etc.).
            if pag.get("type") == "param":
                # If there is no test selector, break.
                test_selector = config["selectors"].get("pagination")
                if not test_selector or not driver.find_elements(By.CSS_SELECTOR, test_selector):
                    break
                # Otherwise a next page exists → increase the counter and search on the next page.
                page += 1
            else:
                # Exit immediately for non-‘param’ pagination types.
                break

        print()
        return products

    finally:
        # Close the browser.
        driver.quit()

