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
def process_squad_link(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    club_header = soup.find('h1')
    club_text = club_header.text.replace("The ", '')
    club_name = " ".join(club_text.split()[:club_text.split().index("rugby")])

    club_player_obj = {}
    club_player_obj[club_name] = []

    squad_table = soup.find('table')
    print(squad_table)
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

def main():
    club_links_json_array = load_club_links()
    player_data = fetch_player_data(club_links_json_array)