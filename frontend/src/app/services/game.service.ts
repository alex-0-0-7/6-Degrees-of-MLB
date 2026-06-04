import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

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
}
