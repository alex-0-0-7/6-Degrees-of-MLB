import { Component, Inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { GameService } from '../services/game.service';
import { HttpClient } from '@angular/common/http';
import { DOCUMENT, LocationStrategy } from '@angular/common';
import playersData from '../../assets/players.json';

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
  nextPlayer: any = null;

  searchQueryStart: any = '';
  searchQueryTarget: any = '';
  searchQueryMove: any = '';

  players: any = {};

  valid: boolean = false;

  attempts: number = 0;
  guesses: any[] = [];
  validGuess: boolean = false;
  validGuesses: any[] = [];

  placeholder: string = 'Search for a player...';

  startYearThreshold: number = 2010; // Only select players from 2010 onwards for better game experience
  endYearThreshold: number = 2025; // Only select players up to 2025 for better game experience

  constructor(@Inject(DOCUMENT) private document: Document,
    private locationStrategy: LocationStrategy, private gameService: GameService, private http: HttpClient) {}

  ngOnInit() {
    // Initialize
    this.players = playersData;
    // console.log(`players: ${JSON.stringify(this.players)}`);
    this.startGame();
  }

  startGame(){
    this.attempts = 0;
    do{
      this.startPlayer = this.players['players'][Math.floor(Math.random() * this.players['players'].length)];
      // console.log(`${this.startPlayer.name} start: ${this.startPlayer.year_start}`);
    // }while(this.startPlayer.year_start < this.startYearThreshold); // Only select players from 2010 onwards for better game experience
    }while(this.startPlayer.year_end !== this.endYearThreshold); // Only select active players for better game experience

    this.targetPlayer = this.searchPlayersTarget(this.startPlayer, this.players['players'][Math.floor(Math.random() * this.players['players'].length)]);
    if(this.targetPlayer.year_start > this.startPlayer.year_start) { // make sure start player is later than target player for better game experience
      const temp = this.startPlayer;
      this.startPlayer = this.targetPlayer;
      this.targetPlayer = temp;
    }
    this.currentPlayer = this.startPlayer;
    this.nextPlayer = this.currentPlayer;
    this.optimalPath = this.gameService.getBFSPath(this.startPlayer.id, this.targetPlayer.id, this.players['players']);
    
    this.placeholder='Search for a player...';


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

  searchPlayers() {
    if (this.searchQueryStart.length < 2) {
      this.searchResultsStart = [];
      return;
    }
    this.searchResultsStart = this.players['players'].filter((player: any) =>
      player.name.toLowerCase().includes(this.searchQueryStart.toLowerCase())    
    );
  }

  searchPlayersTarget(startPlayer: any, targetPlayer: any):any {
    // console.log(`${targetPlayer.name} start: ${targetPlayer.year_start}`);
    // if(targetPlayer.year_start < this.startYearThreshold){ // make sure target player is later than year specified for better game experience

    //   return this.searchPlayersTarget(startPlayer, this.players['players'][Math.floor(Math.random() * this.players['players'].length)]);
    // }
    if(targetPlayer.year_end !== this.endYearThreshold){ // make sure target player is active for better game experience
      return this.searchPlayersTarget(startPlayer, this.players['players'][Math.floor(Math.random() * this.players['players'].length)]);
    }
    for (let team of startPlayer.teams) {
      for(let team2 of targetPlayer.teams) {
        if(team === team2){ // If they share a team, redo the search with a different random target player
          return this.searchPlayersTarget(startPlayer, this.players['players'][Math.floor(Math.random() * this.players['players'].length)]);
        }
      }
    }
    return targetPlayer;
  }

  guessPlayer(){
    this.valid = false;
    let validGuess=false;
    console.log(`guessing ${this.currentPlayer.name}`);

    for(let team of this.currentPlayer.teams) {
      for(let team2 of this.nextPlayer.teams) {
        console.log(`checking guessed player ${this.currentPlayer.name} ${team} vs previous player ${this.nextPlayer.name} ${team2}`);
        if (team === team2){
          validGuess=true;
          break;
        }
      }
      if(validGuess) break;
    }
    console.log(` guessed player ${this.currentPlayer.name} - valid guess: ${validGuess}`);
    if(validGuess){
      this.validGuesses.push(this.currentPlayer);
      for(let team of this.currentPlayer.teams) {
        for(let team2 of this.targetPlayer.teams) {
          console.log(`checking guessed player ${this.currentPlayer.name} ${team} vs target player ${this.targetPlayer.name} ${team2}`);
          if(team === team2 && validGuess){ // If they share a team, player wins
            console.log(`win  ${this.currentPlayer.name} - valid guess: ${validGuess}`);
            this.guesses.push({player: this.currentPlayer, validGuess: validGuess, win: true});
            this.gameWon = true;
            this.showVictoryScreen();
            return;
          }
        }
      }
      this.nextPlayer = this.currentPlayer;
    }
    this.attempts++;
    this.guesses.push({player: this.currentPlayer, validGuess: validGuess, win: false});
    if(this.guesses.length >= 6){
      alert(`Game Over! You have used all 6 attempts. The optimal path was ${this.startPlayer.name} → ${this.optimalPath[this.optimalPath.length - 1].name} → ${this.targetPlayer.name}`);
      this.gameWon = true; // End the game
    }
    this.placeholder = `Search for a player...`;

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
        // this.calculateOptimalPath(game.start_player.id, game.target_player.id);
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
    // this.startPlayer = player;
    this.placeholder = player.name;
    this.currentPlayer = player;
    this.searchResultsStart = [];
    this.searchQueryStart = '';
    this.valid = true;
  }

  selectTargetPlayer(player: any) {
    this.targetPlayer = player;
    this.searchResultsTarget = [];
    this.searchQueryTarget = '';
  }

  showVictoryScreen() {
    const userMoves = this.moves.length;
    const optimalMoves = this.optimalPathLength || 0;
    const comparison = userMoves === optimalMoves ? 'Perfect!' : 
                       userMoves < optimalMoves ? 'Better than optimal!' :
                       `${optimalMoves} moves was optimal`;
    
    // alert(`🎉 Victory! ${userMoves} moves (${comparison}). Optimal path: ${this.startPlayer.name} → ${this.optimalPath[this.optimalPath.length - 1].name} → ${this.targetPlayer.name}`);
  }

  searchBFS(startId: number, endId: number) {
    this.optimalPath = this.gameService.getBFSPath(startId, endId, this.players['players']);
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
    this.guesses = [];
    this.attempts = 0;
    this.validGuesses = [];

    this.startGame();
  }
}
