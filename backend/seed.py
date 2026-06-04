import requests
from app import app
from models import db, Player
from pybaseball import statcast
import pandas as pd

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
        
        all_players = []
        
        for team in teams:
            
            if team['sport']['name'] == 'Major League Baseball':
                team_id = team['id']
                team_name = team['name']
                
                # Fetch roster for each team
                for season in range(int(team['firstYearOfPlay']), int(team['season'])):  # Get all seasons where team is active
                    roster_url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/roster?season={season}&rosterType=active"
                    try:
                        roster_response = requests.get(roster_url, timeout=5)
                        roster_data = roster_response.json()
                        
                        if 'roster' in roster_data:
                            for player_info in roster_data['roster']:
                                person = player_info['person']
                                position = player_info.get('position', {}).get('abbreviation', 'NA')
                                
                                player_data = {
                                    'name': person['fullName'],
                                    'mlb_id': str(person['id']),
                                    'position': position,
                                    'years_active': '2024-2025'
                                }
                                
                                # Avoid duplicates
                                if not any(p['mlb_id'] == player_data['mlb_id'] for p in all_players):
                                    all_players.append(player_data)
                                    
                    except Exception as e:
                        print(f"⚠️  Error fetching roster for {team_name}: {e}")
                        continue
        
        print(f"✓ Successfully fetched {len(all_players)} MLB players")
        return all_players
        
    except Exception as e:
        print(f"❌ Error fetching from MLB StatsAPI: {e}")
        return []

def seed_database():
    with app.app_context():
        # Create all tables first
        db.create_all()
        print("📝 Created database tables")
        
        # Clear existing players
        Player.query.delete()
        db.session.commit()
        print("🗑️  Cleared existing players")
        
        # Fetch real players from MLB API
        players_data = fetch_mlb_players()
        
        if not players_data:
            print("❌ Failed to fetch players. Using fallback data...")
            # Fallback data if API fails
            players_data = [
                {'name': 'Derek Jeter', 'mlb_id': '116539', 'position': 'SS', 'years_active': '1995-2014'},
                {'name': 'Babe Ruth', 'mlb_id': '103353', 'position': 'OF', 'years_active': '1914-1935'},
                {'name': 'Willie Mays', 'mlb_id': '111152', 'position': 'OF', 'years_active': '1951-1973'},
                {'name': 'Hank Aaron', 'mlb_id': '110382', 'position': 'OF', 'years_active': '1954-1976'},
            ]
        
        # Add players to database (limit to 500 for reasonable DB size)
        for player_data in players_data[:500]:
            player = Player(**player_data)
            db.session.add(player)
        
        db.session.commit()
        print(f"✓ Seeded database with {min(len(players_data), 500)} MLB players")

if __name__ == '__main__':
    seed_database()
