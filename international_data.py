import requests
from bs4 import BeautifulSoup
from stats import get_player_stats
from pricer import get_player_price
import json
import time
import traceback

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/91.0.4472.114 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-GB,en;q=0.5',
    'Connection': 'keep-alive',
}

club_links = [
    "https://all.rugby/club/scotland/squad",
    "https://all.rugby/club/south-africa/squad",
    "https://all.rugby/club/england/squad",
    "https://all.rugby/club/argentina/squad",
    "https://all.rugby/club/chile/squad",
    "https://all.rugby/club/australia/squad",
    "https://all.rugby/club/fiji/squad",
    "https://all.rugby/club/france/squad",
    "https://all.rugby/club/wales/squad",
    "https://all.rugby/club/ireland/squad",
    "https://all.rugby/club/japan/squad",
    "https://all.rugby/club/new-zealand/squad",
    "https://all.rugby/club/tonga/squad",
    "https://all.rugby/club/usa/squad"
]

international_data = {}

def get_international_players():
    for link in club_links:
        response = requests.get(link, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        squad_table = None
        club_name = "Unknown Club"

        for h1 in soup.find_all('h1'):
            if 'rugby team' in h1.get_text(separator=" ", strip=True).lower():
                club_name = h1.get_text().split("The ")
                club_name = "".join(club_name).split(" rugby")[0].strip()
                international_data[club_name] = []
                print(f"\n--- Scraping data for {club_name} ---")
                squad_table = h1.find_next('table')
                break

        if squad_table:
            tbody = squad_table.find('tbody') or squad_table
            for tr in tbody.find_all('tr'):
                cells = tr.find_all('td')
                if not cells:
                    continue
                player = tr.find_next('a').text
                international_data[club_name].append(player)


get_international_players()

with open('international_data/data.json', 'w', encoding='utf-8') as f:
    json.dump(international_data, f, indent=4, ensure_ascii=False)