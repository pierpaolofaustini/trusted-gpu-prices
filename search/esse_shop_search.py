import re
from urllib.parse import unquote
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

# Multiple‐page scraping on esseshop.it

opts = Options()
opts.add_argument("--headless")    # start Chrome in headless mode for scraping
opts.add_argument("--disable-gpu") # disable GPU to improve speed
driver = webdriver.Chrome(service=Service(), options=opts)

try:
    url = "https://www.esseshop.it/componenti-hardware-schede-video-c-244-284.html"
    while True:
        driver.get(url)

        # wait for product grid to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.row.row_catalog_products#r_spisok"))
        )

        # collect all product cards
        cards = driver.find_elements(By.CSS_SELECTOR, "div.row.row_catalog_products#r_spisok div.product")
        for idx in range(len(cards)):
            try:
                # re-fetch each card to avoid stale references
                card = driver.find_elements(By.CSS_SELECTOR, "div.row.row_catalog_products#r_spisok div.product")[idx]

                # skip 'arriving' products
                if card.find_elements(By.CSS_SELECTOR, "span.label.label-arriving"):
                    continue

                # extract full product name from slug in href
                try:
                    a = card.find_element(By.CSS_SELECTOR, "a.p_img_href")
                    href = a.get_attribute("href")
                    slug = href.rsplit("/", 1)[-1]
                    name_slug = re.sub(r"-p-\d+\.html$", "", slug)
                    name = unquote(name_slug).replace("-", " ")
                except:
                    name = "—"

                # extract product price
                try:
                    price = card.find_element(By.CSS_SELECTOR, "span.prices span.new_price").text.strip()
                except:
                    price = "Non disponibile"

                print(f"Nome:          {name}")
                print(f"Prezzo:        {price}")
                print("-" * 40)

            except StaleElementReferenceException:
                # skip stale card
                continue

        # navigate to next page or break if none
        try:
            next_link = driver.find_element(By.CSS_SELECTOR, "a.next_page")
            url = next_link.get_attribute("href")
        except NoSuchElementException:
            break

finally:
    # close the browser
    driver.quit()

