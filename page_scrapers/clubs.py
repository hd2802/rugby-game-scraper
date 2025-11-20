from pathlib import Path
import requests
from bs4 import BeautifulSoup
import json

target_leagues = ["Premiership", "Top 14", "United Rugby Championship"]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/129 Safari/537.36"
}

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "out"
CLUB_LINKS_PATH = DATA_DIR / "club_links.json"

SAVE_PATH = BASE_DIR.parent / "out"

""" Helper functions (not called in main, but called in functions that are themselves called in main)"""
def get_club_name(url):
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        club_header = soup.find('h1')
        club_text = club_header.text.replace("The ", '')
        club_name = " ".join(club_text.split()[:club_text.split().index("rugby")])

        return club_name
    except:
        print(f"Error processing squad with url {url}")

""" Runnable functions (ran in main) """
def load_club_links():
    try:
        with open(CLUB_LINKS_PATH) as f:
            d = json.load(f)
            return d
    except:
        print("Error reading data from file")
    
def fetch_clubs_data(links_json_array):
    clubs = []
    for obj in links_json_array:
        for key in obj:
            for url in obj[key]:
                clubs.append(get_club_name(url.replace('/squad','/')))

    return clubs

def save_clubs_data(clubs_data):
    try:
        with open(f"{SAVE_PATH}/clubs_data.json", 'w') as f:
            json.dump(clubs_data, f, ensure_ascii=False, indent=4)
        print(f"Clubs data saved successfully at {SAVE_PATH}")
    except:
        print("Error saving player data")

def main():
    print("===========================================")
    print("Running clubs.py")
    club_links_json_array = load_club_links()
    clubs_data = fetch_clubs_data(club_links_json_array)
    if clubs_data:
        save_clubs_data(clubs_data)
    print("===========================================")