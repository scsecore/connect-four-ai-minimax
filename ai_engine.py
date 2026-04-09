"""
Connect Four AI Engine
Minimax algorithm with Alpha-Beta pruning for optimal move selection.
"""

import math
import random

from game_logic import ROWS, COLS, EMPTY, PLAYER, AI

# Difficulty depth limits
DIFFICULTY_DEPTHS = {
    "easy": 2,
    "medium": 4,
    "hard": 6,
}

# Scoring constants
SCORE_FOUR = 100000
SCORE_THREE = 50
SCORE_TWO = 10
SCORE_CENTER = 6
SCORE_OPP_THREE = -80


def evaluate_window(window, piece):
    """Score a window of 4 cells."""
    opp_piece = PLAYER if piece == AI else AI
    score = 0

    count = window.count(piece)
    empty = window.count(EMPTY)
    opp_count = window.count(opp_piece)

    if count == 4:
        score += SCORE_FOUR
    elif count == 3 and empty == 1:
        score += SCORE_THREE
    elif count == 2 and empty == 2:
        score += SCORE_TWO

    # Penalize opponent threats
    if opp_count == 3 and empty == 1:
        score += SCORE_OPP_THREE
    elif opp_count == 2 and empty == 2:
        score -= 5

    return score


def score_position(board, piece):
    """Evaluate the entire board position for the given piece."""
    score = 0

    # Center column preference — controlling the center is strategically valuable
    center_col = COLS // 2
    center_array = [board[row][center_col] for row in range(ROWS)]
    score += center_array.count(piece) * SCORE_CENTER

    # Horizontal windows
    for row in range(ROWS):
        for col in range(COLS - 3):
            window = [board[row][col + i] for i in range(4)]
            score += evaluate_window(window, piece)

    # Vertical windows
    for row in range(ROWS - 3):
        for col in range(COLS):
            window = [board[row + i][col] for i in range(4)]
            score += evaluate_window(window, piece)

    # Positive diagonal /
    for row in range(3, ROWS):
        for col in range(COLS - 3):
            window = [board[row - i][col + i] for i in range(4)]
            score += evaluate_window(window, piece)

    # Negative diagonal \
    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            window = [board[row + i][col + i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score


def is_terminal_node(game):
    """Check if the game has reached a terminal state."""
    return (
        game.check_winner(PLAYER)
        or game.check_winner(AI)
        or len(game.get_valid_columns()) == 0
    )


def minimax(game, depth, alpha, beta, maximizing_player):
    """
    Minimax algorithm with Alpha-Beta pruning.
    Returns (best_column, score).
    """
    valid_columns = game.get_valid_columns()
    is_terminal = is_terminal_node(game)

    # Base cases
    if depth == 0 or is_terminal:
        if is_terminal:
            if game.check_winner(AI):
                return (None, SCORE_FOUR * 10)
            elif game.check_winner(PLAYER):
                return (None, -SCORE_FOUR * 10)
            else:
                return (None, 0)  # Draw
        else:
            return (None, score_position(game.board, AI))

    # Order columns: prefer center columns for better pruning
    ordered_cols = sorted(valid_columns, key=lambda c: abs(c - COLS // 2))

    if maximizing_player:
        max_score = -math.inf
        best_col = random.choice(valid_columns)

        for col in ordered_cols:
            game_copy = game.copy()
            game_copy.drop_piece(col, AI)
            _, score = minimax(game_copy, depth - 1, alpha, beta, False)

            if score > max_score:
                max_score = score
                best_col = col

            alpha = max(alpha, score)
            if alpha >= beta:
                break  # Beta cutoff

        return best_col, max_score

    else:  # Minimizing player
        min_score = math.inf
        best_col = random.choice(valid_columns)

        for col in ordered_cols:
            game_copy = game.copy()
            game_copy.drop_piece(col, PLAYER)
            _, score = minimax(game_copy, depth - 1, alpha, beta, True)

            if score < min_score:
                min_score = score
                best_col = col

            beta = min(beta, score)
            if alpha >= beta:
                break  # Alpha cutoff

        return best_col, min_score


def get_ai_move(game, difficulty="medium"):
    """
    Get the best move for the AI at the given difficulty level.
    Returns the column index.
    """
    depth = DIFFICULTY_DEPTHS.get(difficulty, 4)
    valid_columns = game.get_valid_columns()

    if not valid_columns:
        return None

    # On easy mode, occasionally make a random move for variety
    if difficulty == "easy" and random.random() < 0.3:
        return random.choice(valid_columns)

    best_col, _ = minimax(game, depth, -math.inf, math.inf, True)
    return best_col
