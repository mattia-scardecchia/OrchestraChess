from enum import Enum
from dataclasses import dataclass
from typing import Optional


class Colour(Enum):
    WHITE = 0
    BLACK = 1

    def flipped(self):
        return Colour.WHITE if self == Colour.BLACK else Colour.BLACK


class Stack:
    """
    Stack class.
    """
    def __init__(self):
        self.stack = []

    def push(self, item):
        """
        Push an item onto the stack.
        """
        self.stack.append(item)

    def pop(self):
        """
        Pop an item off the stack.
        """
        return self.stack.pop()

    def peek(self):
        """
        Peek at the top of the stack.
        """
        return self.stack[-1]

    def is_empty(self):
        """
        Determine if the stack is empty.
        """
        return len(self.stack) == 0


@dataclass
class Move:
    from_row: int
    from_col: int
    to_row: int
    to_col: int
    move_type: Optional[str] = None
    promoted_piece: Optional[str] = None


@dataclass
class InputBuffer:
    selected_piece: Optional[str] = None
    selected_row: Optional[int] = None
    selected_col: Optional[int] = None
    promoted_piece: Optional[str] = None

    def flush(self):
        """
        Flush the input buffer.
        """
        self.selected_piece = None
        self.selected_row = None
        self.selected_col = None
        self.promoted_piece = None
        