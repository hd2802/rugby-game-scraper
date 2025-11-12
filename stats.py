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
        
        # Skip empty rows
        if not cells:
            continue
        
        # Check if first cell contains a season (has "/" in it)
        # If so, update current_season and this row has the season cell
        if "/" in cells[0]:
            current_season = cells[0]
            # Row has season cell, so data starts from index 1
            row_data = dict(zip(headers[1:], cells[1:]))
        else:
            # Row doesn't have season cell (it's using rowspan from previous row)
            # So data starts from index 0, but we skip the season header
            row_data = dict(zip(headers[1:], cells))
        
        # Skip if we don't have a current season set
        if not current_season:
            continue
        
        # Get team and tournament
        team = row_data.get("team", "")
        tournament = row_data.get("tournament", "")
        
        # Skip header-like rows
        text = " ".join(cells).upper()
        if "TOTAL" in text and "TOURNAMENT" not in tournament.upper():
            continue
        
        # Get matches
        matches_str = row_data.get("matches", "0").replace("'", "")
        try:
            matches = int(matches_str) if matches_str.isdigit() else 0
        except ValueError:
            matches = 0
        
        # Skip rows without valid team, tournament, or matches
        if not team or not tournament or matches == 0:
            continue
        
        # Get tries and points
        tries_str = row_data.get("t", "0")
        tries = int(tries_str) if tries_str.isdigit() else 0
        
        points_str = row_data.get("points", "0")
        points = int(points_str) if points_str.isdigit() else 0
        
        data.append({
            "season": current_season,
            "team": team,
            "tournament": tournament,
            "matches": matches,
            "tries": tries,
            "points": points
        })
    
    return data