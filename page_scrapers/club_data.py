from pathlib import Path
import requests
from bs4 import BeautifulSoup
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/129 Safari/537.36"
}

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "out"
CLUB_LINKS_PATH = DATA_DIR / "club_links.json"

SAVE_PATH = BASE_DIR.parent / "out"

def get_club_data(url):
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        club_name = ""

        name_header = soup.find('h1')
        if "rugby team" in name_header.text:
            club_name = name_header.text.replace("The ", "").replace(" rugby team", "")
        
        club_obj = {}
        club_obj["club_name"] = club_name

        tournaments = []

        bold_text = name_header.find_next('b')
        all_links = bold_text.find_all_next('a')
        for link in all_links:
            if "table" in link.attrs['href'] or "result" in link.text:
                continue
            elif "tournament" in link.attrs['href']:
                tournaments.append(link.text)
        club_obj['tournaments'] = tournaments
        return club_obj
    except:
        print(f"Error processing club with url {url}")

def process_club_links(club_links_json):
    club_data = []
    for obj in club_links_json:
        for key in obj:
            for url in obj[key]:
                data = get_club_data(url.replace("/squad", '/'))
                # This doesnt work for some reason
                data['domestic_league'] = key
                if key not in data['tournaments']:
                    data['tournaments'].append(key)
                club_data.append(data)
    return club_data

def load_club_links():
    try:
        with open(CLUB_LINKS_PATH) as f:
            d = json.load(f)
            return d
    except:
        print("Error reading links from file")

def save_club_data(club_data):
    try:
        with open(f"{SAVE_PATH}/club_data.json", 'w') as f:
            json.dump(club_data, f, ensure_ascii=False, indent=4)
        print(f"Player data saved successfully at {SAVE_PATH}")
    except:
        print("Error saving club data")

def main():
    print("===========================================")
    print("Running club_data.py")
    club_links_json_array = load_club_links()
    club_data = process_club_links(club_links_json_array)
    if club_data:
        save_club_data(club_data)
    print("===========================================")
