from page_scrapers import tourn
from page_scrapers import base_player_data
from utils import file_validation

def fetch_club_links():
    if not file_validation.check_file_exists("club_links.json"):
        tourn.main()
    else:
        print("club_links.json already exists - Skipping running tourn.main()")

def player_data_stage_one():
    if not file_validation.check_file_exists("player_data.json"):
        base_player_data.main()
    else:
        print("player_data.json already exists - Skipping running base_player_data.main()")

if __name__ in "__main__":
    #fetch_club_links()
    #player_data_stage_one()

    base_player_data.main()