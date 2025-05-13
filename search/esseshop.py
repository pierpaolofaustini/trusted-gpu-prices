import time
import re
from urllib.parse import unquote
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
    Scrape video cards from esseshop.it, applying optional filters
    on brand and model. Returns a list of dicts with keys:
      - name
      - price
      - availability

    Handles StaleElementReferenceException by re-fetching each card
    element by index and retrying up to 3 times. 
    Prints a live counter.
    """

# None since one or more argument can be empty
def get_products(brand=None, model=None):
    
    # Normalize filters
    brand = brand.lower().strip() if brand else None
    model = model.lower().strip() if model else None

    
    opts = Options()
    opts.add_argument("--headless") # Headless Chrome setup for scraping
    opts.add_argument("--disable-gpu") # Disable GPU to increase speed
    driver = webdriver.Chrome(service=Service(), options=opts)

    products = []
    url = "https://www.esseshop.it/componenti-hardware-schede-video-c-244-284.html"

    try:
        while True:
            driver.get(url)

            # Wait 10s max for product catalog to load (due to injection)
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.row.row_catalog_products#r_spisok"))
            )

            cards_selector = "div.row.row_catalog_products#r_spisok div.product"
            total = len(driver.find_elements(By.CSS_SELECTOR, cards_selector))

            # Iterate by index to avoid stale references
            for idx in range(total):

                # Up to 3 retries for each card if stall  
                retries = 3
                while retries:
                    try:
                        card = driver.find_elements(By.CSS_SELECTOR, cards_selector)[idx]

                        # Skip "arriving" products
                        if card.find_elements(By.CSS_SELECTOR, "span.label.label-arriving"):
                            break

                        # Extract name from slug
                        try:
                            a = card.find_element(By.CSS_SELECTOR, "a.p_img_href")
                            slug = a.get_attribute("href").rsplit("/", 1)[-1]
                            name = unquote(re.sub(r"-p-\d+\.html$", "", slug)).replace("-", " ")
                        except Exception:
                            name = "—"
                        nl = name.lower()

                        # Apply filters
                        if brand and brand not in nl:
                            break
                        if model and model not in nl:
                            break

                        # Extract price
                        try:
                            price = card.find_element(
                                By.CSS_SELECTOR, "span.prices span.new_price"
                            ).text.strip()
                        except Exception:
                            price = "Non disponibile"

                        # Determine availability
                        availability = (
                            "Pronta consegna"
                            if card.find_elements(By.CSS_SELECTOR, "span.label.label-ready")
                            else "Disponibile"
                        )

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
                        break  # skip on any other error

            # Attempt to go to next page; break if none
            try:
                next_link = driver.find_element(By.CSS_SELECTOR, "a.next_page")
                url = next_link.get_attribute("href")
            except NoSuchElementException:
                break

        print()  # newline after counter
        return products

    finally:
        driver.quit()



