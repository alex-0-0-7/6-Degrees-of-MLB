import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { GameService } from '../services/game.service';

@Component({
  selector: 'app-game-board',
  standalone: true,
  imports: [CommonModule, FormsModule],
  providers: [GameService],
  templateUrl: './game-board.component.html',
  styleUrls: ['./game-board.component.css']
})
export class GameBoardComponent implements OnInit {
  gameId: number | null = 1;
  game: any = null;
  moves: any[] = [];
  optimalPath: any[] = [];
  optimalPathLength: number | null = null;
  gameWon: boolean = false;
  
  searchResultsStart: any[] = [];
  searchResultsTarget: any[] = [];
  searchResultsMove: any[] = [];
  
  currentPlayer: any = null;
  connection: string = '';
  loading = false;
  gameStarted = false;
  startPlayer: any = null;
  targetPlayer: any = null;

  constructor(private gameService: GameService) {}

  ngOnInit() {
    // Initialize
  }

  searchPlayersStart() {
    if (this.searchQueryStart.length < 2) {
      this.searchResultsStart = [];
      return;
    }
    this.loading = true;
    this.gameService.searchPlayers(this.searchQueryStart).subscribe({
      next: (results) => {
        this.searchResultsStart = results;
        this.loading = false;
      },
      error: (err) => {
        console.error('Search error:', err);
        this.loading = false;
      }
    });
  }

  searchPlayersTarget() {
    if (this.searchQueryTarget.length < 2) {
      this.searchResultsTarget = [];
      return;
    }
    this.loading = true;
    this.gameService.searchPlayers(this.searchQueryTarget).subscribe({
      next: (results) => {
        this.searchResultsTarget = results;
        this.loading = false;
      },
      error: (err) => {
        console.error('Search error:', err);
        this.loading = false;
      }
    });
  }

  searchPlayersMove() {
    if (this.searchQueryMove.length < 2) {
      this.searchResultsMove = [];
      return;
    }
    this.loading = true;
    this.gameService.searchPlayers(this.searchQueryMove).subscribe({
      next: (results) => {
        this.searchResultsMove = results;
        this.loading = false;
      },
      error: (err) => {
        console.error('Search error:', err);
        this.loading = false;
      }
    });
  }

  startNewGame() {
    if (!this.startPlayer || !this.targetPlayer) {
      alert('Please select both start and target players');
      return;
    }

    this.gameService.createGame(1, this.startPlayer.id, this.targetPlayer.id).subscribe({
      next: (game) => {
        this.game = game;
        this.gameId = game.id;
        this.currentPlayer = game.start_player;
        this.moves = [];
        this.gameWon = false;
        this.gameStarted = true;
        this.startPlayer = null;
        this.targetPlayer = null;
        this.searchResultsStart = [];
        this.searchResultsTarget = [];
        this.searchQueryStart = '';
        this.searchQueryTarget = '';
        
        // Calculate optimal path using BFS
        this.calculateOptimalPath(game.start_player.id, game.target_player.id);
      },
      error: (err) => {
        console.error('Error creating game:', err);
        alert('Error creating game');
      }
    });
  }

  calculateOptimalPath(startId: number, endId: number) {
    this.gameService.findShortestPath(startId, endId).subscribe({
      next: (result) => {
        if (result.found) {
          this.optimalPath = result.path;
          this.optimalPathLength = result.length;
        }
      },
      error: (err) => {
        console.error('Error calculating path:', err);
      }
    });
  }

  useSampleGame() {
    // Create a game with sample IDs (first two players in database)
    this.gameService.createGame(1, 1, 2).subscribe({
      next: (game) => {
        this.game = game;
        this.gameId = game.id;
        this.currentPlayer = game.start_player;
        this.moves = [];
        this.gameStarted = true;
      },
      error: (err) => {
        console.error('Error creating sample game:', err);
        alert('Error creating game. Make sure backend is running and database is seeded!');
      }
    });
  }

  loadGame() {
    if (!this.gameId) return;
    this.gameService.getGame(this.gameId).subscribe({
      next: (game) => {
        this.game = game;
        this.currentPlayer = game.start_player;
        this.loadGameHistory();
      }
    });
  }

  loadGameHistory() {
    if (!this.gameId) return;
    this.gameService.getGameHistory(this.gameId).subscribe({
      next: (data) => {
        this.moves = data.moves;
      }
    });
  }

  selectStartPlayer(player: any) {
    this.startPlayer = player;
    this.searchResultsStart = [];
    this.searchQueryStart = '';
  }

  selectTargetPlayer(player: any) {
    this.targetPlayer = player;
    this.searchResultsTarget = [];
    this.searchQueryTarget = '';
  }

  selectPlayer(player: any) {
    if (!this.currentPlayer || !this.connection) {
      alert('Please enter connection info');
      return;
    }

    if (!this.gameId) return;

    this.gameService.addGameMove(
      this.gameId,
      this.currentPlayer.id,
      player.id,
      this.connection
    ).subscribe({
      next: (move) => {
        this.moves.push(move);
        this.currentPlayer = player;
        this.connection = '';
        this.searchQueryMove = '';
        this.searchResultsMove = [];

        if (this.game && player.id === this.game.target_player.id) {
          this.gameWon = true;
          this.showVictoryScreen();
        }
      },
      error: (err) => {
        console.error('Error adding move:', err);
        alert('Error making move');
      }
    });
  }

  showVictoryScreen() {
    const userMoves = this.moves.length;
    const optimalMoves = this.optimalPathLength || 0;
    const comparison = userMoves === optimalMoves ? 'Perfect!' : 
                       userMoves < optimalMoves ? 'Better than optimal!' :
                       `${optimalMoves} moves was optimal`;
    
    console.log(`🎉 Victory! ${userMoves} moves (${comparison})`);
  }

  resetGame() {
    this.gameStarted = false;
    this.gameWon = false;
    this.game = null;
    this.moves = [];
    this.optimalPath = [];
    this.optimalPathLength = null;
    this.currentPlayer = null;
    this.startPlayer = null;
    this.targetPlayer = null;
    this.searchQueryStart = '';
    this.searchQueryTarget = '';
    this.searchQueryMove = '';
    this.searchResultsStart = [];
    this.searchResultsTarget = [];
    this.searchResultsMove = [];
  }
}
