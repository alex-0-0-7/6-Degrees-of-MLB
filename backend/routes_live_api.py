"""
Optional: Live MLB-StatsAPI routes
Add these routes to routes.py to fetch live data without needing to seed database
"""

import requests
from flask import Blueprint, request, jsonify

api_bp = Blueprint('live_api', __name__, url_prefix='/api')

# ============================================
# Add these routes to your existing routes.py
# ============================================

@api_bp.route('/mlb/players/search', methods=['GET'])
def search_live_players():
    """Search players live from MLB-StatsAPI"""
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify({'error': 'Query too short'}), 400
    
    try:
        # Search using the MLB API
        url = "https://statsapi.mlb.com/api/v1/people"
        params = {'name': query}
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        
        results = []
        if 'people' in data:
            for person in data['people'][:10]:  # Limit to 10 results
                results.append({
                    'id': person['id'],
                    'name': person['fullName'],
                    'mlb_id': str(person['id']),
                    'position': person.get('primaryPosition', {}).get('abbreviation', 'NA'),
                    'team': person.get('currentTeam', {}).get('name', 'Free Agent'),
                    'years_active': person.get('debut', 'Unknown')
                })
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/mlb/teams', methods=['GET'])
def get_teams():
    """Get all MLB teams"""
    try:
        url = "https://statsapi.mlb.com/api/v1/teams"
        response = requests.get(url, timeout=5)
        teams = response.json()['teams']
        
        team_list = [
            {'id': t['id'], 'name': t['name'], 'abbreviation': t.get('abbreviation')}
            for t in teams
        ]
        return jsonify(team_list)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/mlb/team/<int:team_id>/roster', methods=['GET'])
def get_team_roster(team_id):
    """Get roster for a specific team"""
    try:
        url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/roster?rosterType=active"
        response = requests.get(url, timeout=5)
        roster_data = response.json()
        
        if 'roster' in roster_data:
            players = []
            for player_info in roster_data['roster']:
                person = player_info['person']
                position = player_info.get('position', {}).get('abbreviation', 'NA')
                
                players.append({
                    'id': person['id'],
                    'name': person['fullName'],
                    'position': position,
                    'number': player_info.get('jerseyNumber')
                })
            
            return jsonify(players)
        
        return jsonify({'error': 'Team not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/mlb/player/<int:player_id>', methods=['GET'])
def get_player_stats(player_id):
    """Get detailed player information and stats"""
    try:
        url = f"https://statsapi.mlb.com/api/v1/people/{player_id}"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if 'people' in data and len(data['people']) > 0:
            person = data['people'][0]
            
            player_info = {
                'id': person['id'],
                'name': person['fullName'],
                'position': person.get('primaryPosition', {}).get('abbreviation', 'NA'),
                'height': person.get('height'),
                'weight': person.get('weight'),
                'birth_date': person.get('birthDate'),
                'birth_country': person.get('birthCountry'),
                'draft': person.get('draft', {}),
                'hall_of_fame': person.get('hallOfFame', False),
                'active': person.get('active', False)
            }
            
            return jsonify(player_info)
        
        return jsonify({'error': 'Player not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
