import re
from urllib.parse import unquote
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# Single-page scraping for esseshop.it
opts = Options()
opts.add_argument("--headless")       # start Chrome in headless mode
opts.add_argument("--disable-gpu")    # disable GPU to improve speed
driver = webdriver.Chrome(service=Service(), options=opts)

try:
    url = "https://www.esseshop.it/componenti-hardware-schede-video-c-244-284.html"
    driver.get(url)

    # Wait until the product grid is present (max 4s)
    WebDriverWait(driver, 4).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.row.row_catalog_products#r_spisok"))
    )

    # Collect all product cards
    cards = driver.find_elements(By.CSS_SELECTOR, "div.row.row_catalog_products#r_spisok div.product")

    print(f"Trovate {len(cards)} schede sulla pagina.\n")
    for card in cards:
        
        # Extract full product name from slug in href
        try:
            a = card.find_element(By.CSS_SELECTOR, "a.p_img_href")
            href = a.get_attribute("href")
            slug = href.rsplit("/", 1)[-1]                          # take last part
            name_slug = re.sub(r"-p-\d+\.html$", "", slug)         # remove "-p-<id>.html"
            name = unquote(name_slug).replace("-", " ")             # decode & replace dashes
        except:
            name = "—"

        # Extract product price
        try:
            price = card.find_element(By.CSS_SELECTOR, "span.prices span.new_price").text.strip()
        except:
            price = "Non disponibile"

        print(f"Nome:  {name}")
        print(f"Prezzo:{price}")
        print("-" * 40)

finally:
    driver.quit()
