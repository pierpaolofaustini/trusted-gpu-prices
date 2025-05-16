import time
import re
import urllib.parse
from urllib.parse import unquote
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

"""
    Scrape video cards from esseshop.it, applying optional filters
    on brand and model. Returns a list of dicts with keys:
      - name
      - price
      - availability

    Uses the site’s search URL with category filter if brand/model provided,
    else full catalog. Detects whether we’re on search-results (sniperfast)
    or full catalog, adjusts selectors accordingly, retries on stale elements,
    and prints a live counter.
"""

# None defaults allow brand/model to be omitted by the user
def get_products(brand=None, model=None):

    # Normalize filters
    brand = brand.lower().strip() if brand else None
    model = model.lower().strip() if model else None

    # Build initial URL:
    # - if brand or model provided, use search + category filter
    # - otherwise, full video cards catalog

    if brand or model:
        terms = " ".join(filter(None, [brand, model]))
        # encode search terms (spaces → %20)
        search_part = urllib.parse.quote(terms)
        # encode "Schede video " for category filter (ends with space)
        category_part = urllib.parse.quote("Schede video ")
        base_url = (
            f"https://www.esseshop.it/?s={search_part}"
            f"&feat[Categoria][0]={category_part}"
        )
    else:
        base_url = "https://www.esseshop.it/componenti-hardware-schede-video-c-244-284.html"
    url = base_url

    # Headless Chrome setup for scraping
    opts = Options()
    opts.add_argument("--headless")      # Headless Chrome setup for scraping
    opts.add_argument("--disable-gpu")   # Disable GPU to increase speed
    driver = webdriver.Chrome(service=Service(), options=opts)

    products = []
    try:
        while True:
            driver.get(url)

            # Wait up to 15s for search or catalog cards to appear
            try:
                WebDriverWait(driver, 15).until(
                    lambda d: d.find_elements(By.CSS_SELECTOR, "#sniperfast_results_wrapper div.sniperfast_product")
                              or d.find_elements(By.CSS_SELECTOR, "div.row.row_catalog_products#r_spisok div.product")
                )
            except TimeoutException:
                print("\n⚠️ Esseshop page load timed out, aborting.")
                break

            # Detect mode and set selectors
            if driver.find_elements(By.CSS_SELECTOR, "#sniperfast_results_wrapper div.sniperfast_product"):
                cards_sel        = "#sniperfast_results_wrapper div.sniperfast_product"
                name_sel         = "div.sniperfast_prod_name"
                price_sel        = "div.sniperfast_prod_price"
                availability_sel = None
            else:
                cards_sel        = "div.row.row_catalog_products#r_spisok div.product"
                name_sel         = None
                price_sel        = "span.prices span.new_price"
                availability_sel = "span.label.label-ready"

            cards = driver.find_elements(By.CSS_SELECTOR, cards_sel)
            total = len(cards)

            # Iterate by index to avoid stale references
            for idx in range(total):
                retries = 3
                while retries:
                    try:
                        card = driver.find_elements(By.CSS_SELECTOR, cards_sel)[idx]

                        # Skip "arriving" products
                        if card.find_elements(By.CSS_SELECTOR, "span.label.label-arriving"):
                            break

                        # Extract name
                        if name_sel:
                            try:
                                name = card.find_element(By.CSS_SELECTOR, name_sel).text.strip()
                            except NoSuchElementException:
                                name = "—"
                        else:
                            try:
                                href = card.find_element(By.CSS_SELECTOR, "a.p_img_href") \
                                          .get_attribute("href")
                                slug = href.rsplit("/", 1)[-1]
                                name = unquote(re.sub(r"-p-\d+\.html$", "", slug)).replace("-", " ")
                            except Exception:
                                name = "—"
                        nl = name.lower()

                        # Apply brand filter (substring OK)
                        if brand and brand not in nl:
                            break
                        # Apply model filter as whole word
                        if model and not re.search(rf"\b{re.escape(model)}\b", nl):
                            break

                        # Extract price
                        try:
                            price = card.find_element(By.CSS_SELECTOR, price_sel).text.strip()
                        except Exception:
                            price = "Non disponibile"

                        # Determine availability
                        if availability_sel:
                            availability = (
                                "Pronta consegna"
                                if card.find_elements(By.CSS_SELECTOR, availability_sel)
                                else "Disponibile"
                            )
                        else:
                            availability = "Disponibile"

                        # Append and update live counter
                        products.append({
                            "name": name,
                            "price": price,
                            "availability": availability
                        })
                        print(f"\r🔍 Prodotti trovati: {len(products)} 💻", end="", flush=True)

                        break  # success

                    except StaleElementReferenceException:
                        retries -= 1
                        
                        # Give 0.2s before the retry, for browser/DOM to stabilize
                        time.sleep(0.2)
                    except Exception:
                        break

            # Attempt to go to next page if pagination exists
            try:
                next_link = driver.find_element(By.CSS_SELECTOR, "a.next_page")
                url = next_link.get_attribute("href")
            except NoSuchElementException:
                break

        print()  # newline after counter
        return products

    finally:
        driver.quit()






