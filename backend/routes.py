from flask import Blueprint, request, jsonify
from models import db, User, Player, Game, GameMove
from pathfinding import find_shortest_path_between_players, get_path_length

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Player endpoints
@api_bp.route('/players/search', methods=['GET'])
def search_players():
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify({'error': 'Query too short'}), 400
    
    players = Player.query.filter(
        Player.name.ilike(f'%{query}%')
    ).limit(10).all()
    
    return jsonify([p.to_dict() for p in players])

@api_bp.route('/players/<int:player_id>', methods=['GET'])
def get_player(player_id):
    player = Player.query.get_or_404(player_id)
    return jsonify(player.to_dict())

# Game endpoints
@api_bp.route('/games', methods=['POST'])
def create_game():
    data = request.get_json()
    user_id = data.get('user_id')
    start_player_id = data.get('start_player_id')
    target_player_id = data.get('target_player_id')
    
    if not all([user_id, start_player_id, target_player_id]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    game = Game(
        user_id=user_id,
        start_player_id=start_player_id,
        target_player_id=target_player_id
    )
    db.session.add(game)
    db.session.commit()
    
    return jsonify(game.to_dict()), 201

@api_bp.route('/games/<int:game_id>', methods=['GET'])
def get_game(game_id):
    game = Game.query.get_or_404(game_id)
    return jsonify(game.to_dict())

@api_bp.route('/games/<int:game_id>/moves', methods=['POST'])
def add_game_move(game_id):
    game = Game.query.get_or_404(game_id)
    data = request.get_json()
    
    from_player_id = data.get('from_player_id')
    to_player_id = data.get('to_player_id')
    connection = data.get('connection')
    
    if not all([from_player_id, to_player_id, connection]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    move = GameMove(
        game_id=game_id,
        from_player_id=from_player_id,
        to_player_id=to_player_id,
        connection=connection,
        move_number=len(game.moves) + 1
    )
    
    if to_player_id == game.target_player_id:
        game.completed = True
        game.completed_at = __import__('datetime').datetime.utcnow()
    
    game.moves_count = move.move_number
    db.session.add(move)
    db.session.commit()
    
    return jsonify(move.to_dict()), 201

@api_bp.route('/games/<int:game_id>/history', methods=['GET'])
def get_game_history(game_id):
    game = Game.query.get_or_404(game_id)
    return jsonify({
        'game': game.to_dict(),
        'moves': [m.to_dict() for m in game.moves]
    })

# User endpoints
@api_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not all([username, email, password]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    user = User(username=username, email=email, password_hash=password)  # In production, hash password
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@api_bp.route('/users/<int:user_id>/games', methods=['GET'])
def get_user_games(user_id):
    games = Game.query.filter_by(user_id=user_id).all()
    return jsonify([g.to_dict() for g in games])

# Pathfinding endpoints (BFS Algorithm)
@api_bp.route('/path/shortest', methods=['POST'])
def find_shortest_path():
    """Find shortest path between two players using BFS"""
    data = request.get_json()
    start_player_id = data.get('start_player_id')
    end_player_id = data.get('end_player_id')
    
    if not start_player_id or not end_player_id:
        return jsonify({'error': 'Missing player IDs'}), 400
    
    try:
        path = find_shortest_path_between_players(start_player_id, end_player_id)
        
        if path:
            return jsonify({
                'path': path,
                'length': len(path) - 1,
                'found': True
            })
        else:
            return jsonify({
                'path': None,
                'length': None,
                'found': False,
                'message': 'No path found between players'
            }), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/path/length', methods=['GET'])
def get_path_length_endpoint():
    """Get the number of degrees between two players"""
    start_id = request.args.get('start_id', type=int)
    end_id = request.args.get('end_id', type=int)
    
    if not start_id or not end_id:
        return jsonify({'error': 'Missing player IDs'}), 400
    
    try:
        length = get_path_length(start_id, end_id)
        
        if length is not None:
            return jsonify({'degrees': length})
        else:
            return jsonify({'degrees': None, 'message': 'No path found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Health check
@api_bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})
