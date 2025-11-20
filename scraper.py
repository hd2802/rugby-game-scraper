from page_scrapers import tourn
from utils import file_validation

def fetch_club_links():
    if not file_validation.check_file_exists("club_links.json"):
        tourn.main()
    else:
        print("club_links.json already exists - No need to run tourn.main()")

if __name__ in "__main__":
    fetch_club_links()