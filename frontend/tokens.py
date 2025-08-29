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
    DECREMENT = auto()
    PLUS_SIGN = auto()
    ASTERISK = auto()
    FORWARD_SLASH = auto()
    MINUS_SIGN = auto()
    PERCENT_SIGN = auto()


Token = NamedTuple("Token", [("type", TokenType), ("value", "str")])
