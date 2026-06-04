from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    games = db.relationship('Game', backref='player', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

class Player(db.Model):
    __tablename__ = 'players'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    mlb_id = db.Column(db.String(50), unique=True, nullable=False)
    position = db.Column(db.String(10))
    team = db.Column(db.String(50))
    years_active = db.Column(db.String(50))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'mlb_id': self.mlb_id,
            'position': self.position,
            'team': self.team,
            'years_active': self.years_active
        }

class Game(db.Model):
    __tablename__ = 'games'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    target_player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    moves_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    start_player = db.relationship('Player', foreign_keys=[start_player_id])
    target_player = db.relationship('Player', foreign_keys=[target_player_id])
    moves = db.relationship('GameMove', backref='game', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'start_player': self.start_player.to_dict(),
            'target_player': self.target_player.to_dict(),
            'completed': self.completed,
            'moves_count': self.moves_count,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class GameMove(db.Model):
    __tablename__ = 'game_moves'
    
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    from_player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    to_player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    connection = db.Column(db.String(255), nullable=False)  # Shared team/era
    move_number = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    from_player = db.relationship('Player', foreign_keys=[from_player_id])
    to_player = db.relationship('Player', foreign_keys=[to_player_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'game_id': self.game_id,
            'from_player': self.from_player.to_dict(),
            'to_player': self.to_player.to_dict(),
            'connection': self.connection,
            'move_number': self.move_number,
            'created_at': self.created_at.isoformat()
        }
