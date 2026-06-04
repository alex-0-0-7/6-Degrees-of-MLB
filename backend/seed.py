import requests
from app import app
from models import db, Player
from pybaseball import statcast, playerid_lookup, batting_stats_bref
import pandas as pd
import json
import numpy as np

def fetch_mlb_players():
    """
    Fetch MLB player data from statsapi.mlb.com
    Gets all active players from recent seasons
    """
    try:
        print("🔄 Fetching MLB player data from StatsAPI...")
        
        # Fetch all teams first
        teams_url = "https://statsapi.mlb.com/api/v1/teams"
        teams_response = requests.get(teams_url)
        teams = teams_response.json()['teams']
        mlb_teams=[team for team in teams if team['sport']['name'] == 'Major League Baseball']
        with open('teams.json', 'w') as f:
           json.dump(mlb_teams, f)
        
        all_players = []

        # return all_players
        for season in range(2020, 2027):
            for team in mlb_teams:     
                # Fetch roster for each team
                    roster_url = f"https://statsapi.mlb.com/api/v1/teams/{team['id']}/roster?season={season}&rosterType=active"
                    try:
                        roster_response = requests.get(roster_url, timeout=5)
                        roster_data = roster_response.json()
                        
                        if 'roster' in roster_data:
                            for player_info in roster_data['roster']:
                                person = player_info['person']
                                
                                result = next((obj for obj in all_players if obj['id'] == str(person['id'])), None)
                                if not result:
                                    player_data = {
                                        'name': person['fullName'],
                                        'id': str(person['id']),
                                        'year_start': season,
                                        'year_end': season,
                                        'teams':[f"{str(season)} {team['name']}"]
                                    }
                                    all_players.append(player_data)
                                else:
                                    result['year_end'] = season
                                    result['teams'].append(f"{str(season)} {team['name']}")
                                    
                    except Exception as e:
                        print(f"⚠️  Error fetching roster for {team['name']}: {e}")
                        continue
        
        print(f"✓ Successfully fetched {len(all_players)} MLB players")
        return all_players
        
    except Exception as e:
        print(f"❌ Error fetching from MLB StatsAPI: {e}")
        return []

def seed_database():
    with app.app_context():
        
        # Fetch real players from MLB API
        players_data = fetch_mlb_players()
        
        if not players_data:
            print("❌ Failed to fetch players. Using fallback data...")
            # Fallback data if API fails
            players_data = [
            ]
        
        # Add players to database (limit to 500 for reasonable DB size)
        # for player_data in players_data[:500]:
        #     player = Player(**player_data)
        #     db.session.add(player)

        with open('players.json', 'w') as f:
           json.dump(players_data, f)
        
        # db.session.commit()
        print(f"✓ Seeded database with {min(len(players_data), 500)} MLB players")

if __name__ == '__main__':
    seed_database()
