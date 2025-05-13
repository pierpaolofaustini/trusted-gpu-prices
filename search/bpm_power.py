import time
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

    Handles StaleElementReferenceException by re-fetching each card
    element by index and retrying up to 3 times. Prints a live counter.
    """

# None since one or more argument can be left empty by the user
def get_products(brand=None, model=None):
    
    # Normalize filters
    brand = brand.lower().strip() if brand else None
    model = model.lower().strip() if model else None

    opts = Options()
    opts.add_argument("--headless") # Headless Chrome setup for scraping
    opts.add_argument("--disable-gpu") # Disable GPU to increase speed
    driver = webdriver.Chrome(service=Service(), options=opts)

    products = []
    base_url = "https://www.bpm-power.com/it/online/componenti-pc/schede-video"
    page = 1

    try:
        while True:
            driver.get(f"{base_url}?page={page}")

            # Wait 10s max for product grid to load (due to injection)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#divTopGridListProduct"))
            )

            # End pagination when no page items found
            if not driver.find_elements(By.CSS_SELECTOR, "ul.pagination li.page-item"):
                break

            cards_selector = "#divGridProducts .bordoCat"
            total = len(driver.find_elements(By.CSS_SELECTOR, cards_selector))

            # Iterate by index to avoid stale references
            for idx in range(total):

                # Up to 3 retries for each card if stall  
                retries = 3
                while retries:
                    try:
                        card = driver.find_elements(By.CSS_SELECTOR, cards_selector)[idx]

                        # Extract name
                        try:
                            name = card.find_element(
                                By.CSS_SELECTOR, "h4.nomeprod_category"
                            ).text.strip()
                        except NoSuchElementException:
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
                        break  # skip on any other error

            # Move on to the next page
            page += 1

        print()  # newline after counter
        return products

    finally:
        driver.quit()

