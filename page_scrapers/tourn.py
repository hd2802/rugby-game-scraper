from pathlib import Path
import requests
from bs4 import BeautifulSoup
import json

""" 
This code will read from tournament_links.txt, with each link, the code will find the link for each club in the league.
Then each url of the club will be saved in a new file in out/club_links.json that stores the data as such:

    [
        {"Premiership": [
            "https://northhamptonsaintsurl.com"
        ]}
    ]
"""

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/129 Safari/537.36"
}

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"
TOURN_LINKS_PATH = DATA_DIR / "tourn_links.txt"

SAVE_PATH = BASE_DIR.parent / "out"

""" Helper functions (not called in main, but called in functions that are themselves called in main)"""
def get_club_links(url):
    full_club_links = []
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    header = soup.find('h1').text.split()
    year_index = header.index('2025') if '2025' in header else header.index('2026')
    league_name = " ".join(header[:year_index])

    teams_header = soup.find('h2')
    
    all_links = teams_header.find_all_next('a')
    for a in all_links:
        if "Table" in a.text:
            break
        else:
            full_club_links.append(f"https://all.rugby{a.attrs['href']}")
    
    league_object = { league_name: full_club_links }
    return league_object

""" Runnable functions (ran in main) """
def load_seed_links(path=TOURN_LINKS_PATH):
    try:
        with open(path, "r") as f:
            return [line.strip() for line in f if line.strip()]
        print(f"{TOURN_LINKS_PATH} file read successfully")
    except:
        print(f"Error reading league links from {TOURN_LINKS_PATH}")

def process_seed_links(link_array):
    try:
        print("Processing tournament links")
        league_data = []
        for url in link_array:
            league_data.append(get_club_links(url))
        print("Tournament links process successfully")
        return league_data
    except:
        print("Error processing tournament links")


def save_league_data(league_data):
    try:
        with open(f"{SAVE_PATH}/club_links.json", 'w') as f:
            json.dump(league_data, f, ensure_ascii=False, indent=4)
        print(f"Club links saved successfully at {SAVE_PATH}")
    except:
        print("Error saving club links")

def main():
    print("===========================================")
    print("Running tourn.py")
    seed_links = load_seed_links()
    league_data = process_seed_links(seed_links)
    if league_data:
        save_league_data(league_data)
    print("===========================================")