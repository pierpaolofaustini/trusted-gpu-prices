from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# Single page search successful 

opts = Options()
opts.add_argument("--headless") # setup headless Chrome - better for scraping 
opts.add_argument("--disable-gpu") # for faster search
driver = webdriver.Chrome(service=Service(), options=opts)

try:
    # Open the website at the correct endpoint
    driver.get("https://www.bpm-power.com/it/online/componenti-pc/schede-video")

    # Wait until all is injected (probably using Vue.js)
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#divGridProducts .bordoCat"))
    )

    # Iterating the correct DOM structure on bpm-power
    cards = driver.find_elements(By.CSS_SELECTOR, "#divGridProducts .bordoCat")
    for card in cards:
        # Name
        try:
            name = card.find_element(By.CSS_SELECTOR, "h4.nomeprod_category").text.strip()
        except:
            name = "—"

        # Price
        try:
            price = card.find_element(By.CSS_SELECTOR, "p.prezzoCat").text.strip()
        except:
            price = "Non disponibile"

        # Availability search
        has_si     = len(card.find_elements(By.CSS_SELECTOR, "span.dispoSi")) > 0
        has_ultimi = len(card.find_elements(By.CSS_SELECTOR, "span.dispoUltimi")) > 0
        availability = "Disponibile" if (has_si or has_ultimi) else "Non disponibile"

        print(f"Nome:          {name}")
        print(f"Prezzo:        {price}")
        print(f"Disponibilità: {availability}")
        print("-" * 40)

# Close the browser 
finally:
    driver.quit()

