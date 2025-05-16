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
    NoSuchElementException
)

"""
    Scrape video cards from bpm-power.com, applying optional filters
    on brand and model. Returns a list of dicts with keys:
      - name
      - price
      - availability

    Uses the site’s search URL if brand/model provided, else full catalog.
    Handles StaleElementReferenceException by re-fetching each card
    element by index and retrying up to 3 times. Prints a live counter.
"""

# None defaults allow brand/model to be omitted by the user
def get_products(brand=None, model=None):

    # Normalize filters
    brand = brand.lower().strip() if brand else None
    model = model.lower().strip() if model else None

    # Build initial URL: search if filters present, else full catalog
    if brand or model:
        terms = "+".join(filter(None, [brand, model]))
        base_url = f"https://www.bpm-power.com/it/ricerca?k={urllib.parse.quote_plus(terms)}"
    else:
        base_url = "https://www.bpm-power.com/it/online/componenti-pc/schede-video"
    page = 1

    # Headless Chrome setup for scraping
    opts = Options()
    opts.add_argument("--headless")      # Headless Chrome to speed up scraping
    opts.add_argument("--disable-gpu")   # Disable GPU for stability
    driver = webdriver.Chrome(service=Service(), options=opts)

    products = []
    try:
        while True:
            url = f"{base_url}&page={page}" if "?" in base_url else f"{base_url}?page={page}"
            driver.get(url)

            # Wait up to 15s for at least one product card to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#divGridProducts .bordoCat"))
            )

            # Stop if no pagination (after page 1) on full-catalog
            if page > 1 and not driver.find_elements(By.CSS_SELECTOR, "ul.pagination li.page-item"):
                break

            cards_sel = "#divGridProducts .bordoCat"
            total = len(driver.find_elements(By.CSS_SELECTOR, cards_sel))

            # Iterate by index to avoid stale references
            for idx in range(total):

                # Up to 3 retries for each card if stall  
                retries = 3
                while retries:
                    try:
                        card = driver.find_elements(By.CSS_SELECTOR, cards_sel)[idx]

                        # Skip sold-out items
                        if card.find_elements(By.CSS_SELECTOR, "span.dispoNo"):
                            break

                        # Extract name
                        try:
                            name = card.find_element(
                                By.CSS_SELECTOR, "h4.nomeprod_category"
                            ).text.strip()
                        except NoSuchElementException:
                            name = "—"
                        nl = name.lower()

                        # Only real video cards (must contain "scheda video")
                        if "scheda video" not in nl:
                            break

                        # Brand filter
                        if brand and brand not in nl:
                            break
                        # Model filter as whole word
                        if model and not re.search(rf"\b{re.escape(model)}\b", nl):
                            break

                        # Extract price
                        try:
                            price = card.find_element(
                                By.CSS_SELECTOR, "p.prezzoCat"
                            ).text.strip()
                        except Exception:
                            price = "Not available"

                        # Determine availability
                        has_si     = bool(card.find_elements(By.CSS_SELECTOR, "span.dispoSi"))
                        has_ultimi = bool(card.find_elements(By.CSS_SELECTOR, "span.dispoUltimi"))
                        availability = "Available" if (has_si or has_ultimi) else "Unavailable"

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
                        break  # skip any other error

            # Move on to the next page
            page += 1

        print()  # newline after counter
        return products

    finally:
        driver.quit()


