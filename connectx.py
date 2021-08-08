"""Implementation of the ConnectX game, environment, and callbacks."""

from enum import Enum, auto

import numpy as np


class MoveResult(Enum):
    """Enum for the result of a move."""

    NORMAL = auto()
    WIN = auto()
    DRAW = auto()
    INVALID = auto()

    def __repr__(self):
        return "<%s.%s>" % (self.__class__.__name__, self.name)


def _to_char(piece):
    return "⬛" if piece == 0 else ("🟡" if piece == 1 else "🔴")


class ConnectX:
    """A generalized Connect Four game."""

    def __init__(self, rows=6, cols=7, win_length=4):
        self.rows = rows
        self.cols = cols
        self.win_length = win_length
        self.reset()

    def reset(self):
        """Reset the board."""
        self.board = np.zeros((self.rows, self.cols), dtype=np.int32)
        self._stack_height = np.zeros(self.cols, dtype=np.int32)
        self.player = 1

    def step(self, action):
        """Make a move."""
        if self._stack_height[action] >= self.rows:
            return MoveResult.INVALID

        row = self._stack_height[action]
        self.board[row, action] = self.player
        self._stack_height[action] += 1

        if self._is_win(row, action):
            result = MoveResult.WIN
        elif np.all(self.board[-1]):
            result = MoveResult.DRAW
        else:
            result = MoveResult.NORMAL

        self.player *= -1

        return result

    def get_observation(self, player):
        """Return the board from the perspective of the given player."""
        board_player = np.where(self.board == player, 1.0, 0.0)
        board_opponent = np.where(self.board == -player, 1.0, 0.0)
        return np.array([board_player, board_opponent])

    def _is_horizontal_win(self, row, col):
        length = 1
        if col > 0:
            for piece in self.board[row, col - 1 :: -1]:
                if piece == self.board[row, col]:
                    length += 1
                    if length >= self.win_length:
                        return True
                else:
                    break
        for piece in self.board[row, col + 1 :]:
            if piece == self.board[row, col]:
                length += 1
                if length >= self.win_length:
                    return True
            else:
                break
        return False

    def _is_vertical_win(self, row, col):
        length = 1
        if row > 0:
            for piece in self.board[row - 1 :: -1, col]:
                if piece == self.board[row, col]:
                    length += 1
                    if length >= self.win_length:
                        return True
                else:
                    break
        return False

    def _is_diagonal1_win(self, row, col):
        length = 1
        diag = self.board.diagonal(col - row)
        index = min(row, col)
        if index > 0:
            for piece in diag[index - 1 :: -1]:
                if piece == self.board[row, col]:
                    length += 1
                    if length >= self.win_length:
                        return True
                else:
                    break
        for piece in diag[index + 1 :]:
            if piece == self.board[row, col]:
                length += 1
                if length >= self.win_length:
                    return True
            else:
                break
        return False

    def _is_diagonal2_win(self, row, col):
        length = 1
        flipped_row = self.rows - 1 - row
        diag = np.flipud(self.board).diagonal(col - flipped_row)
        index = min(flipped_row, col)
        if index > 0:
            for piece in diag[index - 1 :: -1]:
                if piece == self.board[row, col]:
                    length += 1
                    if length >= self.win_length:
                        return True
                else:
                    break
        for piece in diag[index + 1 :]:
            if piece == self.board[row, col]:
                length += 1
                if length >= self.win_length:
                    return True
            else:
                break
        return False

    def _is_win(self, row, col):
        return (
            self._is_vertical_win(row, col)
            or self._is_horizontal_win(row, col)
            or self._is_diagonal1_win(row, col)
            or self._is_diagonal2_win(row, col)
        )

    def __str__(self):
        return "\n".join(
            "".join(_to_char(piece) for piece in row) for row in np.flipud(self.board)
        )
