from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
import random
import os
from .snake_ladder_game import SnakeAndLadderGame

app_routes = Blueprint('app_routes', __name__)

# Game state storage
games = {}

@app_routes.route('/')
def index():
    return render_template('index.html')

@app_routes.route('/new-game', methods=['GET', 'POST'])
def new_game():
    if request.method == 'POST':
        player_count = int(request.form.get('player_count'))
        player_names = []
        
        for i in range(player_count):
            name = request.form.get(f'player_{i+1}')
            player_names.append(name)
        
        game_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
        game = SnakeAndLadderGame()
        
        for name in player_names:
            game.player_names.append(name)
            game.players[name] = 0
        
        games[game_id] = {
            'game': game,
            'current_player_idx': 0,
            'winner': None,
            'last_roll': None,
            'message': f"Game started! {game.player_names[0]}'s turn."
        }
        
        session['game_id'] = game_id
        return redirect(url_for('app_routes.play_game'))
    
    return render_template('new_game.html')

@app_routes.route('/play')
def play_game():
    game_id = session.get('game_id')
    if not game_id or game_id not in games:
        return redirect(url_for('app_routes.index'))
    
    game_data = games[game_id]
    game = game_data['game']
    board_data = prepare_board_data(game)
    
    return render_template(
        'game.html',
        board_data=board_data,
        players=game.players,
        current_player=game.player_names[game_data['current_player_idx']],
        winner=game_data['winner'],
        last_roll=game_data['last_roll'],
        message=game_data['message']
    )

@app_routes.route('/roll-dice', methods=['POST'])
def roll_dice():
    game_id = session.get('game_id')
    if not game_id or game_id not in games:
        return redirect(url_for('app_routes.index'))
    
    game_data = games[game_id]
    game = game_data['game']
    
    if game_data['winner']:
        return jsonify({'redirect': url_for('app_routes.play_game')})
    
    current_player_idx = game_data['current_player_idx']
    current_player = game.player_names[current_player_idx]
    
    dice_roll = game.roll_dice()
    game_data['last_roll'] = dice_roll
    
    message = f"{current_player} rolled a {dice_roll}."
    
    if game.players[current_player] == 0 and dice_roll != 6:
        message += f" {current_player} needs to roll a 6 to start. Try again next turn!"
    else:
        if game.players[current_player] == 0:
            message += f" {current_player} rolled a 6 and enters the game!"
            game.players[current_player] = 1
            new_position = game.move_player(current_player, dice_roll - 1)
        else:
            new_position = game.move_player(current_player, dice_roll)
        
        message += f" {current_player} moved to {new_position}."
        
        if new_position != game.players[current_player]:
            if new_position > game.players[current_player]:
                message += f" Climbed a ladder to {game.players[current_player]}!"
            else:
                message += f" Bitten by a snake! Moved down to {game.players[current_player]}."
        
        if game.players[current_player] == 100:
            game_data['winner'] = current_player
            message += f" 🎉 {current_player} won the game! 🎉"
    
    game_data['message'] = message
    game_data['current_player_idx'] = (current_player_idx + 1) % len(game.player_names)
    
    return jsonify({'redirect': url_for('app_routes.play_game')})

def prepare_board_data(game):
    board_data = []
    for i in range(10):
        row = []
        for j in range(10):
            row_num = 9 - i
            cell_num = row_num * 10 + (j + 1) if row_num % 2 == 0 else row_num * 10 + (10 - j)
            cell = {
                'number': cell_num,
                'players': [],
                'has_snake': cell_num in game.snakes,
                'has_ladder': cell_num in game.ladders,
                'snake_to': game.snakes.get(cell_num),
                'ladder_to': game.ladders.get(cell_num)
            }
            for player, position in game.players.items():
                if position == cell_num:
                    cell['players'].append(player)
            row.append(cell)
        board_data.append(row)
    return board_data
