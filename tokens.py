from enum import Enum, auto
from typing import NamedTuple


class TokenType(Enum):
    IDENTIFIER = auto()
    CONSTANT = auto()
    INT_KEYWORD = auto()
    VOID_KEYWORD = auto()
    RETURN = auto()
    L_PAREN = auto()
    R_PAREN = auto()
    L_BRACE = auto()
    R_BRACE = auto()
    SEMICOLON = auto()
    COMPLEMENT = auto()
    NEGATION = auto()
    DECREMENT = auto()


Token = NamedTuple("Token", [("type", TokenType), ("value", "str")])
