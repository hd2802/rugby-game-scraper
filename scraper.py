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

league_links = [
    "https://all.rugby/tournament/npc/table",
    "https://all.rugby/tournament/mlr/table",
    "https://all.rugby/tournament/league-one-d1/table",
    "https://all.rugby/tournament/premiership/table",
    "https://all.rugby/tournament/urc/table",
    "https://all.rugby/tournament/champ-rugby/table",
    "https://all.rugby/tournament/top-14/table",
    "https://all.rugby/tournament/pro-d2/table",
    "https://all.rugby/tournament/nationale/table",
]

extra_links = [
    "https://all.rugby/club/cheetahs/squad",
    "https://all.rugby/club/black-lion/squad"
]

super_links = [
    "https://all.rugby/club/brumbies/squad",
    "https://all.rugby/club/chiefs/squad",
    "https://all.rugby/club/crusaders/squad",
    "https://all.rugby/club/fijian-drua/squad",
    "https://all.rugby/club/highlanders/squad",
    "https://all.rugby/club/hurricanes/squad",
    "https://all.rugby/club/moana-pasifika/squad",
    "https://all.rugby/club/reds/squad",
    "https://all.rugby/club/waratahs/squad",
    "https://all.rugby/club/western-force/squad"
]

league_urls = {}
league_clubs = {}

def format_name(name):
    particles = {'du', 'de', 'van', 'der', 'den', 'ter', 'ten', 'la', 'le'}

    def capitalize_part(part):
        return '-'.join(
            word.lower() if word.lower() in particles else word.capitalize()
            for word in part.split('-')
        )

    parts = name.strip().split()
    formatted_parts = [capitalize_part(part) for part in parts]

    return ' '.join(formatted_parts)

def get_player_data(cells):
    return {
        'name': cells[1].text.strip() if len(cells) > 3 else '',
        'position': cells[2].text.strip() if len(cells) > 1 else '',
        'dob': cells[4].text.strip() if len(cells) > 1 else '',
        'height': cells[5].text.strip().replace('\xa0', '') if len(cells) > 1 else '',
        'weight': cells[6].text.strip().replace('\xa0', '') if len(cells) > 1 else '',
        'contract': cells[9].text.strip() if len(cells) > 2 else '',
        'nation': cells[0].find_next('img').attrs['alt'] if len(cells) > 2 else '',
    }

def get_club_links():
    for link in league_links:
        response = requests.get(link, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        league_name = soup.find('h1').get_text(strip=True)
        league_name = league_name.split(' Standings')[0].split(' Logs')[0]
        league_urls[league_name] = []

        standing_table = soup.find('table')
        if standing_table:
            tbody = standing_table.find('tbody') or standing_table
            for tag in tbody.find_all('a'):
                relative = tag.attrs['href']
                club_url = f"https://all.rugby{relative}squad"
                league_urls[league_name].append(club_url)

    league_urls['Extra Clubs'] = extra_links
    league_urls['Super Rugby Pacific'] = super_links


def get_squad_data():
    for league, club_links in league_urls.items():
        league_clubs[league] = []
        for link in club_links:
            response = requests.get(link, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            squad_table = None
            club_name = "Unknown Club"
            for h1 in soup.find_all('h1'):
                if 'rugby team' in h1.get_text(separator=" ", strip=True).lower():
                    club_name = h1.get_text().split("The ")
                    club_name = "".join(club_name).split(" rugby")[0].strip()
                    print(f"\n--- Scraping data for {club_name} ({league}) ---")
                    league_clubs[league].append(club_name)
                    squad_table = h1.find_next('table')
                    break

            club_players = []
            if squad_table:
                tbody = squad_table.find('tbody') or squad_table
                for tr in tbody.find_all('tr'):
                    cells = tr.find_all('td')
                    if not cells:
                        continue
                    player_link = tr.find_next('a').attrs['href']
                    player = get_player_data(cells)
                    player['club'] = club_name
                    player['league'] = league
                    player['value'] = get_player_price(cells, league)

                    try:
                        print(f"  Scraping data for {player['name']} ...")
                        player['playing_history'] = get_player_stats(f"https://all.rugby{player_link}")
                    except Exception as e:
                        print(f"Error getting stats for {player['name']} ({club_name}): {e}")
                        traceback.print_exc()
                        player['playing_history'] = None  # continue gracefully
                        continue

                    club_players.append(player)

            filename = f"data/{club_name.lower().replace(' ', '_')}_players.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(club_players, f, indent=4, ensure_ascii=False)

            print(f"Saved {len(club_players)} players for {club_name} → {filename}")


def run():
    start_time = time.perf_counter()
    print("Starting rugby data scraping...\n")

    try:
        get_club_links()
        get_squad_data()
    except Exception as e:
        print(f"Critical error in run(): {e}")
        traceback.print_exc()

    elapsed = time.perf_counter() - start_time
    print(f"\n Scraping completed in {elapsed:.2f} seconds.")
