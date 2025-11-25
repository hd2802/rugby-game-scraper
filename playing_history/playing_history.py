from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

""" These are helper functions, not directly called by main """
def create_driver(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)
    return driver

def click_cookies_button(driver):
    try:
        accept_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//span[contains(text(), 'Accept all')]")
            )
        )
        accept_btn.click()
    except:
        pass

def click_overall_button_fetch_soup(url):
    driver = create_driver(url)

    wait = WebDriverWait(driver, 10)
    click_cookies_button(driver)

    overall_li = wait.until(EC.element_to_be_clickable((By.ID, "saisonNav_ov")))
    driver.execute_script("arguments[0].click();", overall_li)

    wait.until(EC.presence_of_element_located((By.ID, "saison_ov")))

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.close()
    return soup

""" These are called directly by the main of this file"""
def get_playing_history(url):
    soup = click_overall_button_fetch_soup(url)
    tbody = soup.find('tbody')
    rows = tbody.find_all('tr')
    parsed = []

    current = {
        "season": None,
        "team": None,
    }

    for tr in rows:
        cells = tr.find_all("td")
        record = {}

        ci = 0

        if cells[ci].get("class") and "tdsaison" in cells[ci]["class"]:
            current["season"] = cells[ci].get_text(strip=True)
            ci += 1
        record["season"] = current["season"]

        if len(cells) > ci and cells[ci].find('img'):
            ci += 1
        
        if len(cells) > ci and cells[ci].get("class") and "tdclub" in cells[ci]["class"]:
            current["team"] = cells[ci].get_text(strip=True)
            ci += 1
        record["team"] = current["team"]

        rest = cells[ci:]

        fields = [
            "tournament", "matches", "W_D_L", "starter",
            "tries", "drops", "penalties", "conversions",
            "points", "pen_cards", "minutes"
        ]

        for f, td in zip(fields, rest):
            record[f] = td.get_text(strip=True)
        
        parsed.append(record)

    return parsed

def process_url(url):
    try:
        data = get_playing_history(url)
        return data
    except Exception as e:
        print(f"Error processing {url}")
        return []