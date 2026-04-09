"""
Connect Four Game Logic
Handles board representation, move validation, and win detection.
"""

ROWS = 6
COLS = 7
EMPTY = 0
PLAYER = 1  # Human (Red)
AI = 2      # AI (Yellow)


class ConnectFourGame:
    def __init__(self):
        self.board = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
        self.current_player = PLAYER
        self.game_over = False
        self.winner = None
        self.last_move = None
        self.move_count = 0

    def get_valid_columns(self):
        """Return list of columns that still have empty slots."""
        return [col for col in range(COLS) if self.board[0][col] == EMPTY]

    def is_valid_move(self, col):
        """Check if a column has space for another disc."""
        return 0 <= col < COLS and self.board[0][col] == EMPTY

    def get_next_open_row(self, col):
        """Return the lowest empty row in the given column."""
        for row in range(ROWS - 1, -1, -1):
            if self.board[row][col] == EMPTY:
                return row
        return None

    def drop_piece(self, col, piece):
        """
        Drop a piece into the specified column.
        Returns (row, col) of the placed piece, or None if invalid.
        """
        if not self.is_valid_move(col) or self.game_over:
            return None

        row = self.get_next_open_row(col)
        if row is None:
            return None

        self.board[row][col] = piece
        self.last_move = (row, col)
        self.move_count += 1

        # Check for winner
        if self.check_winner(piece):
            self.game_over = True
            self.winner = piece

        # Check for draw
        if self.move_count >= ROWS * COLS and not self.game_over:
            self.game_over = True
            self.winner = None  # Draw

        return (row, col)

    def check_winner(self, piece):
        """Check if the given piece has won the game."""
        # Horizontal
        for row in range(ROWS):
            for col in range(COLS - 3):
                if all(self.board[row][col + i] == piece for i in range(4)):
                    return True

        # Vertical
        for row in range(ROWS - 3):
            for col in range(COLS):
                if all(self.board[row + i][col] == piece for i in range(4)):
                    return True

        # Diagonal (positive slope /)
        for row in range(3, ROWS):
            for col in range(COLS - 3):
                if all(self.board[row - i][col + i] == piece for i in range(4)):
                    return True

        # Diagonal (negative slope \)
        for row in range(ROWS - 3):
            for col in range(COLS - 3):
                if all(self.board[row + i][col + i] == piece for i in range(4)):
                    return True

        return False

    def get_winning_cells(self, piece):
        """Return the list of cells that form the winning line."""
        # Horizontal
        for row in range(ROWS):
            for col in range(COLS - 3):
                cells = [(row, col + i) for i in range(4)]
                if all(self.board[r][c] == piece for r, c in cells):
                    return cells

        # Vertical
        for row in range(ROWS - 3):
            for col in range(COLS):
                cells = [(row + i, col) for i in range(4)]
                if all(self.board[r][c] == piece for r, c in cells):
                    return cells

        # Diagonal /
        for row in range(3, ROWS):
            for col in range(COLS - 3):
                cells = [(row - i, col + i) for i in range(4)]
                if all(self.board[r][c] == piece for r, c in cells):
                    return cells

        # Diagonal \
        for row in range(ROWS - 3):
            for col in range(COLS - 3):
                cells = [(row + i, col + i) for i in range(4)]
                if all(self.board[r][c] == piece for r, c in cells):
                    return cells

        return []

    def is_draw(self):
        """Check if the board is full with no winner."""
        return self.move_count >= ROWS * COLS and self.winner is None

    def copy(self):
        """Return a deep copy of the game state."""
        new_game = ConnectFourGame()
        new_game.board = [row[:] for row in self.board]
        new_game.current_player = self.current_player
        new_game.game_over = self.game_over
        new_game.winner = self.winner
        new_game.last_move = self.last_move
        new_game.move_count = self.move_count
        return new_game

    def to_dict(self):
        """Serialize the game state to a dictionary."""
        winning_cells = []
        if self.winner is not None:
            winning_cells = self.get_winning_cells(self.winner)

        return {
            "board": self.board,
            "current_player": self.current_player,
            "game_over": self.game_over,
            "winner": self.winner,
            "last_move": self.last_move,
            "move_count": self.move_count,
            "valid_columns": self.get_valid_columns(),
            "winning_cells": winning_cells,
            "is_draw": self.is_draw(),
        }
