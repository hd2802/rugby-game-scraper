import scraper
import time
import requests

def post_data(players, league_clubs):
    success_count = 0
    failure_count = 0
    failed = []

    for league in league_clubs:
        resp = requests.post(
            'http://localhost:3003/api/leagues',
            json={
                "name": league
            },
            headers={'Content-Type': 'application/json'}
        )

        club_array = league_clubs[league]

        for club in club_array:
            club_resp = requests.post(
                "http://localhost:3003/api/clubs",
                json={
                    "name": club,
                    "league_name": league
                },
                headers={'Content-Type': 'application/json'}
            )
    
    for player in players:
        player_data = player.copy()
        
        player_resp = requests.post(
            "http://localhost:3003/api/players",
            json=player_data,
            headers={'Content-Type': 'application/json'}
        )

        if player_resp.status_code in (200, 201):
            print(f"Created player {player_data['name']}")
            success_count += 1
        
        if player_resp.status_code not in (200, 201):
            print(f"Failed to create player {player_data['name']}: {player_resp.text}")
            failed.append(f"{player_data['name']}: {player_resp.text}")
            failure_count += 1
    
    return (success_count, failure_count, failed)

def main():
    players, league_clubs = scraper.run()
    s,f, failed = post_data(players, league_clubs)

    start_time = time.time()
    print(f"Successful operations {s}")
    print(f"Unsuccessful operations {f}")
    print(f"Out of {len(players)} total operations")
    print("----- FAILED OPERATIONS ------- ")
    print(failed)
    print("------------------------------- ")
    print(f"Runtime: {time.time() - start_time}")

if __name__ == "__main__":
   main()