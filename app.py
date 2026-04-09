"""
Connect Four AI — Flask Application
Serves the frontend and provides API endpoints for game interaction.
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from game_logic import ConnectFourGame, PLAYER, AI
from ai_engine import get_ai_move

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

# In-memory game store (single-player, single session for simplicity)
games = {}


def get_or_create_game(game_id="default", difficulty="medium"):
    """Retrieve existing game or create a new one."""
    if game_id not in games:
        games[game_id] = {
            "game": ConnectFourGame(),
            "difficulty": difficulty,
            "scores": {"player": 0, "ai": 0, "draws": 0},
        }
    return games[game_id]


# ─── Serve Frontend ───────────────────────────────────────────────────────────


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


# ─── API Endpoints ────────────────────────────────────────────────────────────


@app.route("/api/new-game", methods=["POST"])
def new_game():
    """Start a new game, preserving the scoreboard."""
    data = request.get_json() or {}
    difficulty = data.get("difficulty", "medium")
    game_id = data.get("game_id", "default")

    session = get_or_create_game(game_id, difficulty)
    session["game"] = ConnectFourGame()
    session["difficulty"] = difficulty

    return jsonify({
        "status": "ok",
        "message": "New game started",
        "game": session["game"].to_dict(),
        "scores": session["scores"],
        "difficulty": session["difficulty"],
    })


@app.route("/api/make-move", methods=["POST"])
def make_move():
    """Handle a human player's move, then let AI respond."""
    data = request.get_json() or {}
    col = data.get("column")
    game_id = data.get("game_id", "default")

    if col is None:
        return jsonify({"status": "error", "message": "No column specified"}), 400

    session = get_or_create_game(game_id)
    game = session["game"]

    if game.game_over:
        return jsonify({
            "status": "error",
            "message": "Game is already over",
            "game": game.to_dict(),
        }), 400

    if not game.is_valid_move(col):
        return jsonify({
            "status": "error",
            "message": f"Column {col} is full or invalid",
            "game": game.to_dict(),
        }), 400

    # Player move
    player_pos = game.drop_piece(col, PLAYER)
    response = {
        "status": "ok",
        "player_move": {"row": player_pos[0], "col": player_pos[1]},
        "ai_move": None,
        "game": game.to_dict(),
        "scores": session["scores"],
    }

    # Update scores if player won
    if game.game_over:
        if game.winner == PLAYER:
            session["scores"]["player"] += 1
        elif game.winner is None:
            session["scores"]["draws"] += 1
        response["game"] = game.to_dict()
        response["scores"] = session["scores"]
        return jsonify(response)

    # AI move
    ai_col = get_ai_move(game, session["difficulty"])
    if ai_col is not None:
        ai_pos = game.drop_piece(ai_col, AI)
        response["ai_move"] = {"row": ai_pos[0], "col": ai_pos[1]}

    # Update scores if AI won or draw
    if game.game_over:
        if game.winner == AI:
            session["scores"]["ai"] += 1
        elif game.winner is None:
            session["scores"]["draws"] += 1

    response["game"] = game.to_dict()
    response["scores"] = session["scores"]
    return jsonify(response)


@app.route("/api/state", methods=["GET"])
def get_state():
    """Get the current game state."""
    game_id = request.args.get("game_id", "default")
    session = get_or_create_game(game_id)
    return jsonify({
        "game": session["game"].to_dict(),
        "scores": session["scores"],
        "difficulty": session["difficulty"],
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
