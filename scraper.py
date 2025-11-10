import requests
from bs4 import BeautifulSoup
from stats import get_player_stats
from pricer import get_player_price

headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-GB,en;q=0.5',
        'Connection': 'keep-alive',
    }

league_links = [
    #"https://all.rugby/tournament/npc/table",
    #"https://all.rugby/tournament/mlr/table",
    #"https://all.rugby/tournament/super-rugby-pacific/table",
    #"https://all.rugby/tournament/league-one-d1/table",
    "https://all.rugby/tournament/premiership/table",
    #"https://all.rugby/tournament/urc/table",
    #"https://all.rugby/tournament/champ-rugby/table",
    #"https://all.rugby/tournament/top-14/table",
    #"https://all.rugby/tournament/pro-d2/table",
    #"https://all.rugby/tournament/nationale/table",
]

# For holding per-league urls
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
    player_data = {
        'name': cells[1].text.strip() if len(cells) > 3 else '',
        'position': cells[2].text.strip() if len(cells) > 1 else '',
        'dob': cells[4].text.strip() if len(cells) > 1 else '',
        'height': cells[5].text.strip().replace('\xa0', '') if len(cells) > 1 else '',
        'weight': cells[6].text.strip().replace('\xa0', '') if len(cells) > 1 else '',
        'contract': cells[9].text.strip() if len(cells) > 2 else '',
        'nation': cells[0].find_next('img').attrs['alt'] if len(cells) > 2 else '',
    }
    #print(player_data)
    return player_data

def get_club_links():
    current_league = ""
    for link in league_links:
        response = requests.get(link, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        headings = soup.find('h1')
        current_league = str(headings.text).split(' Standings')[0]
        current_league = str(current_league).split(" Logs")[0]
        
        league_urls[current_league] = []

        standing_table = soup.find('table')

        if standing_table:
            tbody = standing_table.find('tbody') or standing_table
            club_tag = tbody.find_all('a')
            for tag in club_tag:
                relative = (tag.attrs)['href']
                club_url = f"https://all.rugby{relative}squad"
                league_urls[current_league].append(club_url)
                

def get_squad_data():
    players = []
    for league, club_links in league_urls.items():
        league_clubs[league] = []
        for link in club_links:
            response = requests.get(link, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            squad_table = None
            for h1 in soup.find_all('h1'):
                if 'rugby team' in h1.get_text(separator=" ", strip=True):
                    club_name = str(h1.text).split("The ")
                    club_name = "".join(club_name).split(" rugby")[0]
                    print(f"Scraping data for {club_name}")
                    league_clubs[league].append(club_name)
                    squad_table = h1.find_next('table')
                    break
            
            if squad_table:
                tbody = squad_table.find('tbody') or squad_table
                for tr in tbody.find_all('tr'):
                    cells = tr.find_all('td')
                    player_link = tr.find_next('a').attrs['href']
                    if not cells:
                        continue
                    player = get_player_data(cells)
                    player['club'] = club_name
                    price = get_player_price(cells, league)
                    player['value'] = price
                    player['league'] = league
                    print(f"Scraping data for {player['name']}")
                    player['playing_history'] = get_player_stats(f"https://all.rugby{player_link}")
                    players.append(player)
                    print(player)
            
            for h2 in soup.find_all('h2'):
                h2_text = h2.get_text(separator=" ", strip=True).lower()
                if 'academy' not in h2_text:
                    continue
                if 'contract' in h2_text or 'ended' in h2_text:
                    continue
                academy_table = h2.find_next('table')
                if not academy_table:
                    continue
                tbody = academy_table.find('tbody') or academy_table
                for tr in tbody.find_all('tr'):
                    player_link = tr.find_next('a').attrs['href']
                    cells = tr.find_all('td')
                    if not cells:
                        continue
                    player = get_player_data(cells)
                    player['club'] = club_name
                    price = get_player_price(cells, league)
                    player['value'] = price
                    player['league'] = league
                    player['playing_history'] = get_player_stats(f"https://all.rugby{player_link}")
                    players.append(player)
    
    return players
            
def run():
    get_club_links()
    players = get_squad_data()
    return (players, league_clubs)

players, league_clubs = run()