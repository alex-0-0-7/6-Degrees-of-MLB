import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

interface Player {
    id: number;
    name: string;
    teams: string[];
}

interface TeamYear{
  year: number;
  team: string;
}

@Injectable({
  providedIn: 'root'
})

export class GameService {
  
  private apiUrl = 'http://localhost:5000/api';

  constructor(private http: HttpClient) {}

  searchPlayers(query: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/players/search?q=${query}`);
  }

  getPlayer(id: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/players/${id}`);
  }

  createGame(userId: number, startPlayerId: number, targetPlayerId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/games`, {
      user_id: userId,
      start_player_id: startPlayerId,
      target_player_id: targetPlayerId
    });
  }

  getGame(gameId: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/games/${gameId}`);
  }

  addGameMove(gameId: number, fromPlayerId: number, toPlayerId: number, connection: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/games/${gameId}/moves`, {
      from_player_id: fromPlayerId,
      to_player_id: toPlayerId,
      connection: connection
    });
  }

  getGameHistory(gameId: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/games/${gameId}/history`);
  }

  // BFS Pathfinding
  findShortestPath(startPlayerId: number, endPlayerId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/path/shortest`, {
      start_player_id: startPlayerId,
      end_player_id: endPlayerId
    });
  }

  getPathLength(startPlayerId: number, endPlayerId: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/path/length?start_id=${startPlayerId}&end_id=${endPlayerId}`);
  }

  // BFS
  getBFSPath(startPlayerId: number, endPlayerId: number, players: any[]): any {
    if (startPlayerId === endPlayerId) {
      const player = players.find(p => p.id === startPlayerId);
      return player ? [player] : null;
    }

    // Quick lookup maps
    const playerMap = new Map<number, Player>();
    const teamToPlayers = new Map<string, Player[]>();

    for (const player of players) {
      playerMap.set(player.id, player);

      for (const team of player.teams) {
        if (!teamToPlayers.has(team)) {
          teamToPlayers.set(team, []);
        }
        teamToPlayers.get(team)!.push(player);
      }
    }

    const visited = new Set<number>();
    const queue: number[] = [startPlayerId];

    // Tracks how we reached each player
    const previous = new Map<number, number>();

    visited.add(startPlayerId);

    while (queue.length > 0) {
      const currentPlayerId = queue.shift()!;
      const currentPlayer = playerMap.get(currentPlayerId);

      if (!currentPlayer) {
        continue;
      }

      // Find all neighboring players through shared teams
      for (const team of currentPlayer.teams) {
        const teammates = teamToPlayers.get(team) ?? [];

        for (const teammate of teammates) {
          if (visited.has(teammate.id)) {
            continue;
          }

          visited.add(teammate.id);
          previous.set(teammate.id, currentPlayerId);

          if (teammate.id === endPlayerId) {
            // Reconstruct shortest path
            const path: Player[] = [];
            let current: number | undefined = endPlayerId;

            while (current) {
              const player = playerMap.get(current);
              if (player) {
                path.push(player);
              }

              current = previous.get(current);
            }

            return path.reverse();
          }

          queue.push(teammate.id);
        }
      }
    }
    return null; // No path found
  }

  truncateTeams(teams: TeamYear[]): string[] {
    const result: string[] = [];

    let start = teams[0].year;
    let end = teams[0].year;
    let currentTeam = teams[0].team;

    for (let i = 1; i < teams.length; i++) {
      const item = teams[i];

      if (item.team === currentTeam && item.year === end + 1) {
        end = item.year;
      } else {
        result.push(start === end
            ? `${start} ${currentTeam}`
            : `${start} - ${end} ${currentTeam}`
        );

        start = end = item.year;
        currentTeam = item.team;
      }
    }

    result.push(start === end
        ? `${start} ${currentTeam}`
        : `${start} - ${end} ${currentTeam}`
    );

    return result;
  }
}
