from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

# Multiple page search successful

opts = Options()
opts.add_argument("--headless")  # start Chrome in headless mode for scraping
opts.add_argument("--disable-gpu")  # disable GPU to improve speed
driver = webdriver.Chrome(service=Service(), options=opts)

try:
    base_url = "https://www.bpm-power.com/it/online/componenti-pc/schede-video"
    page = 1

    while True:
        # navigate directly to the paged URL
        url = f"{base_url}?page={page}"
        driver.get(url)

        # wait up to 4 seconds for the main container to appear
        WebDriverWait(driver, 4).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#divTopGridListProduct"))
        )

        # check pagination items; break if none (past last real page)
        li_pages = driver.find_elements(By.CSS_SELECTOR, "ul.pagination li.page-item")
        if not li_pages:
            print(f"Nessuna voce di paginazione a pagina {page} → fine scraping.")
            break

        # collect all product cards
        cards = driver.find_elements(By.CSS_SELECTOR, "#divGridProducts .bordoCat")
        total_cards = len(cards)
        print(f"\n=== Pagina {page} — {total_cards} schede trovate ===")

        # handle potential stale references
        for idx in range(total_cards):
            try:
                # re-fetch the card element by index to avoid stale references
                card = driver.find_elements(By.CSS_SELECTOR, "#divGridProducts .bordoCat")[idx]

                # extract product name
                try:
                    name = card.find_element(By.CSS_SELECTOR, "h4.nomeprod_category").text.strip()
                except:
                    name = "—"

                # extract product price
                try:
                    price = card.find_element(By.CSS_SELECTOR, "p.prezzoCat").text.strip()
                except:
                    price = "Non disponibile"

                # determine availability
                has_si     = bool(card.find_elements(By.CSS_SELECTOR, "span.dispoSi"))
                has_ultimi = bool(card.find_elements(By.CSS_SELECTOR, "span.dispoUltimi"))
                availability = "Disponibile" if (has_si or has_ultimi) else "Non disponibile"

                print(f"Nome:          {name}")
                print(f"Prezzo:        {price}")
                print(f"Disponibilità: {availability}")
                print("-" * 40)

            except StaleElementReferenceException:
                print(f"[!] Scheda {idx+1}/{total_cards} è stale. Skippo.")

        # move on to the next page
        page += 1

    print("\nScraping completato.")

finally:
    # close the browser
    driver.quit()

