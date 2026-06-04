"""
Breadth-First Search (BFS) pathfinding algorithm
Finds the shortest path between two MLB players through shared teammates
"""
from collections import deque
from typing import List, Tuple, Optional, Set
from models import Player, db

class PlayerGraph:
    """Graph representation of MLB players and their shared team connections"""
    
    def __init__(self):
        self.graph = {}  # player_id -> set of connected player_ids
        self.connections = {}  # (player_id1, player_id2) -> connection_info
    
    def build_from_teams(self):
        """Build player graph from shared teams"""
        # Get all players
        players = Player.query.all()
        
        # Group players by team
        teams = {}
        for player in players:
            team = player.team
            if team not in teams:
                teams[team] = []
            teams[team].append(player.id)
        
        # Connect players who share a team
        for team, player_ids in teams.items():
            for i, player_id1 in enumerate(player_ids):
                if player_id1 not in self.graph:
                    self.graph[player_id1] = set()
                
                for player_id2 in player_ids[i+1:]:
                    # Connect both directions
                    self.graph[player_id1].add(player_id2)
                    
                    if player_id2 not in self.graph:
                        self.graph[player_id2] = set()
                    self.graph[player_id2].add(player_id1)
                    
                    # Store connection info
                    key = tuple(sorted([player_id1, player_id2]))
                    self.connections[key] = {
                        'team': team,
                        'type': 'shared_team'
                    }
    
    def get_neighbors(self, player_id: int) -> List[int]:
        """Get all players connected to this player"""
        return list(self.graph.get(player_id, set()))
    
    def get_connection_info(self, player_id1: int, player_id2: int) -> dict:
        """Get connection info between two players"""
        key = tuple(sorted([player_id1, player_id2]))
        return self.connections.get(key, {})

def bfs_shortest_path(start_id: int, end_id: int, graph: PlayerGraph) -> Optional[List[int]]:
    """
    Find shortest path between two players using BFS
    Returns list of player IDs representing the path
    """
    if start_id == end_id:
        return [start_id]
    
    visited = set()
    queue = deque([(start_id, [start_id])])
    visited.add(start_id)
    
    while queue:
        current_id, path = queue.popleft()
        
        # Check neighbors
        for neighbor_id in graph.get_neighbors(current_id):
            if neighbor_id == end_id:
                return path + [neighbor_id]
            
            if neighbor_id not in visited:
                visited.add(neighbor_id)
                queue.append((neighbor_id, path + [neighbor_id]))
    
    # No path found
    return None

def get_path_details(path: List[int]) -> List[dict]:
    """
    Convert path of player IDs to detailed path with connection info
    Returns list of dicts with player info and connection
    """
    if not path:
        return []
    
    details = []
    graph = PlayerGraph()
    graph.build_from_teams()
    
    # Add first player
    player = Player.query.get(path[0])
    details.append({
        'player_id': player.id,
        'name': player.name,
        'position': player.position,
        'team': player.team,
        'connection': None
    })
    
    # Add subsequent players with connections
    for i in range(1, len(path)):
        current_id = path[i]
        prev_id = path[i-1]
        
        player = Player.query.get(current_id)
        connection_info = graph.get_connection_info(prev_id, current_id)
        
        details.append({
            'player_id': player.id,
            'name': player.name,
            'position': player.position,
            'team': player.team,
            'connection': f"Played for {connection_info.get('team', 'same team')}"
        })
    
    return details

def find_shortest_path_between_players(start_id: int, end_id: int) -> Optional[List[dict]]:
    """
    Main function to find shortest path and return detailed info
    """
    graph = PlayerGraph()
    graph.build_from_teams()
    
    path = bfs_shortest_path(start_id, end_id, graph)
    
    if path:
        return get_path_details(path)
    
    return None

def get_path_length(start_id: int, end_id: int) -> Optional[int]:
    """Get the number of degrees (hops) between two players"""
    graph = PlayerGraph()
    graph.build_from_teams()
    
    path = bfs_shortest_path(start_id, end_id, graph)
    
    if path:
        return len(path) - 1  # Number of connections, not players
    
    return None
