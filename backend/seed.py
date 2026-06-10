import requests
from app import app
from models import db, Player
from pybaseball import statcast, playerid_lookup, batting_stats_bref
import pandas as pd
import json
import numpy as np
from unidecode import unidecode

def fetch_mlb_players():
    """
    Fetch MLB player data from statsapi.mlb.com
    Gets players from recent seasons
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
        playerid_hash={}  # To track unique players by ID
        player_name_hash={}  # To track unique players by name (for cases where 2 different players have the same name)

        # return all_players
        for season in range(2000, 2026):  # Fetch players from 2000 to 2025
            for team in mlb_teams:     
                # Fetch roster for each team
                    roster_url = f"https://statsapi.mlb.com/api/v1/teams/{team['id']}/roster?season={season}&rosterType=active"
                    try:
                        roster_response = requests.get(roster_url, timeout=5)
                        roster_data = roster_response.json()
                        
                        if 'roster' in roster_data:
                            for player_info in roster_data['roster']:
                                person = player_info['person']
                                
                                # result = next((obj for obj in all_players if obj['id'] == str(person['id'])), None)
                                result = playerid_hash.get(str(person['id']), None)
                                if not result:
                                    # If we see a player with the same name but different ID, mark both as not unique
                                    if player_name_hash.get(person['fullName'], {}) and player_name_hash[person['fullName']]['id'] != str(person['id']):
                                        for i in range(len(all_players)):
                                            if all_players[i]['name'] == person['fullName']:
                                                all_players[i]['unique_name'] = False
                                    player_data = {
                                        'name': unidecode(person['fullName']),
                                        'id': str(person['id']),
                                        'year_start': season,
                                        'year_end': season,
                                        'teams':[f"{str(season)} {team['name']}"],
                                        # Handle players who have the same name but are different people (e.g. 2 Will Smiths) - if we see the same name but different ID, mark both as not unique
                                        'unique_name': False if player_name_hash.get(person['fullName'], {}) and player_name_hash[person['fullName']]['id'] != str(person['id']) else True
                                    }
                                    all_players.append(player_data)
                                    playerid_hash[str(person['id'])] = player_data
                                    player_name_hash[person['fullName']] = player_data
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

        with open('../frontend/src/assets/players.json', 'w') as f:
           json.dump({"players": players_data}, f)
        
        # db.session.commit()
        # print(f"✓ Seeded database with {min(len(players_data), 500)} MLB players")

if __name__ == '__main__':
    seed_database()
