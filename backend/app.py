import os
from flask import Flask
from flask_cors import CORS
from models import db, User, Player, Game, GameMove
from routes import api_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mlb_game.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-secret-key'

db.init_app(app)
CORS(app)

app.register_blueprint(api_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
