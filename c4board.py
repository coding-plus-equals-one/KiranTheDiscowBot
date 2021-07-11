"""The Four in a Row game."""

from enum import Enum, auto


class NoValue(Enum):
    """Enum that doesn't print out values of the enumeration."""

    def __repr__(self):
        return "<%s.%s>" % (self.__class__.__name__, self.name)


class Color(NoValue):
    """Enum for the two colors."""

    YELLOW = auto()
    RED = auto()


class MoveResult(NoValue):
    """Enum for the result of a move."""

    NORMAL = auto()
    YELLOW_WIN = auto()
    RED_WIN = auto()
    DRAW = auto()
    INVALID = auto()


BOARD_WIDTH = 7
BOARD_HEIGHT = 6
WIN_LENGTH = 4

BLANK = "⬛"
YELLOW_PIECE = "🟡"
RED_PIECE = "🔴"


class C4Board:
    """A Four in a Row board."""

    def __init__(self):
        self.board = [[] for _ in range(BOARD_WIDTH)]
        self.move_count = 0

    @property
    def turn(self):
        """Return the color of the player who moves next."""
        return Color.YELLOW if self.move_count % 2 == 0 else Color.RED

    def _is_horizontal_win(self, row, column):
        length = 1
        for i in range(column - 1, -1, -1):
            try:
                if self.board[i][row] == self.board[column][row]:
                    length += 1
                    if length >= WIN_LENGTH:
                        return True
                else:
                    break
            except IndexError:
                break
        for i in range(column + 1, BOARD_WIDTH):
            try:
                if self.board[i][row] == self.board[column][row]:
                    length += 1
                    if length >= WIN_LENGTH:
                        return True
                else:
                    break
            except IndexError:
                break
        return False

    def _is_vertical_win(self, row, column):
        length = 1
        if row > 0:
            for piece in self.board[column][row - 1 :: -1]:
                if piece == self.board[column][row]:
                    length += 1
                    if length >= WIN_LENGTH:
                        return True
                else:
                    break
        for piece in self.board[column][row + 1 :]:
            if piece == self.board[column][row]:
                length += 1
                if length >= WIN_LENGTH:
                    return True
            else:
                break
        return False

    def _is_diagonal1_win(self, row, column):
        length = 1
        for i, j in zip(range(column - 1, -1, -1), range(row - 1, -1, -1)):
            try:
                if self.board[i][j] == self.board[column][row]:
                    length += 1
                    if length >= WIN_LENGTH:
                        return True
                else:
                    break
            except IndexError:
                break
        for i, j in zip(range(column + 1, BOARD_WIDTH), range(row + 1, BOARD_HEIGHT)):
            try:
                if self.board[i][j] == self.board[column][row]:
                    length += 1
                    if length >= WIN_LENGTH:
                        return True
                else:
                    break
            except IndexError:
                break
        return False

    def _is_diagonal2_win(self, row, column):
        length = 1
        for i, j in zip(range(column - 1, -1, -1), range(row + 1, BOARD_HEIGHT)):
            try:
                if self.board[i][j] == self.board[column][row]:
                    length += 1
                    if length >= WIN_LENGTH:
                        return True
                else:
                    break
            except IndexError:
                break
        for i, j in zip(range(column + 1, BOARD_WIDTH), range(row - 1, -1, -1)):
            try:
                if self.board[i][j] == self.board[column][row]:
                    length += 1
                    if length >= WIN_LENGTH:
                        return True
                else:
                    break
            except IndexError:
                break
        return False

    def _is_win(self, row, column):
        return (
            self._is_vertical_win(row, column)
            or self._is_horizontal_win(row, column)
            or self._is_diagonal1_win(row, column)
            or self._is_diagonal2_win(row, column)
        )

    def move(self, column):
        """Drop a piece into column column."""

        if len(self.board[column]) >= BOARD_HEIGHT:
            return MoveResult.INVALID

        color = self.turn
        row = len(self.board[column])
        self.board[column].append(color)
        self.move_count += 1

        if self._is_win(row, column):
            return (
                MoveResult.YELLOW_WIN if color is Color.YELLOW else MoveResult.RED_WIN
            )
        if self.move_count == BOARD_WIDTH * BOARD_HEIGHT:
            return MoveResult.DRAW
        return MoveResult.NORMAL

    def _char_at(self, row, column):
        try:
            return (
                YELLOW_PIECE if self.board[column][row] == Color.YELLOW else RED_PIECE
            )
        except IndexError:
            return BLANK

    def __str__(self):
        return (
            "\n".join(
                "".join(self._char_at(i, j) for j in range(BOARD_WIDTH))
                for i in range(BOARD_HEIGHT - 1, -1, -1)
            )
            + "\n"
            + "".join(
                str(i) + "\N{VARIATION SELECTOR-16}\N{COMBINING ENCLOSING KEYCAP}"
                for i in range(BOARD_WIDTH)
            )
            + (YELLOW_PIECE if self.turn == Color.YELLOW else RED_PIECE)
        )
