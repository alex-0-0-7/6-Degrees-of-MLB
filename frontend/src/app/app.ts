import { Component } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { GameBoardComponent } from './components/game-board.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [HttpClientModule, GameBoardComponent],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  title = '6 Degrees of MLB';
}
