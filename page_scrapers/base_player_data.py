from pathlib import Path
import requests
from bs4 import BeautifulSoup
import json

""" 
This code will read from club_links.json with each link, the code will find the table data for each player in the club.
Then each data of the players will be saved in a new file in out/player_data.json that stores the data as such:

    [
        { "Bath Rubgy": [
            {
                "name": "Will STUART",
                ...,
                "url": "https://,,,,,,.com"
            }
        ]}
    ]
"""

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/129 Safari/537.36"
}

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "out"
CLUB_LINKS_PATH = DATA_DIR / "club_links.json"

SAVE_PATH = BASE_DIR.parent / "out"

""" Helper functions (not called in main, but called in functions that are themselves called in main)"""
def process_player_row(cells):
    print(f"Processing player {cells[1].text.strip()}")
    return {
        'name': cells[1].text.strip() if len(cells) > 3 else '',
        'url': f"https://all.rugby{cells[1].find_next('a').attrs['href']}",
        'position': cells[2].text.strip() if len(cells) > 1 else '',
        'dob': cells[4].text.strip() if len(cells) > 1 else '',
        'height': cells[5].text.strip().replace('\xa0', '') if len(cells) > 1 else '',
        'weight': cells[6].text.strip().replace('\xa0', '') if len(cells) > 1 else '',
        'contract': cells[9].text.strip() if len(cells) > 2 else '',
        'nation': cells[0].find_next('img').attrs['alt'] if len(cells) > 2 else '',
    }

def process_squad_link(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    club_header = soup.find('h1')
    club_text = club_header.text.replace("The ", '')
    club_name = " ".join(club_text.split()[:club_text.split().index("rugby")])

    print(f"Scraping data for {club_name}")

    club_player_obj = {}
    club_player_obj[club_name] = []

    squad_table = soup.find('table')
    for row in squad_table.find_all('tr')[1:]:
        cells = row.find_all('td')
        club_player_obj[club_name].append(process_player_row(cells))

    return club_player_obj

""" Runnable functions (ran in main) """
def load_club_links():
    with open(CLUB_LINKS_PATH) as f:
        d = json.load(f)
        return d
    
def fetch_player_data(links_json_array):
    full_data = []
    for obj in links_json_array:
        for key in obj:
            for url in obj[key]:
                data = process_squad_link(url)
                full_data.append(data)
    return full_data

def save_player_data(player_data):
    try:
        with open(f"{SAVE_PATH}/player_data.json", 'w') as f:
            json.dump(player_data, f, ensure_ascii=False, indent=4)
        print(f"Player data saved successfully at {SAVE_PATH}")
    except:
        print("Error saving player data")

def main():
    club_links_json_array = load_club_links()
    player_data = fetch_player_data(club_links_json_array)
    save_player_data(player_data)