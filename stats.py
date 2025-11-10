from selenium import webdriver
from bs4 import BeautifulSoup
import json
import time

def get_player_stats(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(1)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    header = soup.find('h2', string=lambda t: t and "Overall" in t)
    if not header:
        print("No overall stats found")
        return None
    
    table = header.find_next("table")
    rows = table.find_all('tr')

    headers = [th.get_text(strip=True).lower() for th in rows[0].find_all('th')]

    data = []
    current_season = ""

    for row in rows[1:]:
        cells = [td.get_text(strip=True) for td in row.find_all('td')]

        if not cells or len(cells) < len(headers):
            continue

        text = " ".join(cells).upper()
        if any(word in text for word in ["TEAM", "TOURNAMENT", "TOTAL"]):
            continue

        if "/" in cells[0]:
            current_season = cells[0]
        
        row_data = dict(zip(headers, cells))
        team = row_data.get("team", "")
        tournament = row_data.get("tournament", "")
        matches = row_data.get("matches", "0").replace("'", "")

        try:
            matches = int(matches) if matches.isdigit() else 0
        except ValueError:
            matches = 0
        
        if not team or not tournament or matches == 0:
            continue
        
        tries = row_data.get("t", "0")
        tries = int(tries) if tries.isdigit() else 0
        points = row_data.get("points", "0")
        points = int(points) if points.isdigit() else 0

        data.append({
            "season": current_season,
            "team": team,
            "tournament": tournament,
            "matches": matches,
            "tries": tries,
            "points": points
        })

    return data