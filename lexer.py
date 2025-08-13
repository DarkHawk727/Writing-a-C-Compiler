import re
from typing import List

from tokens import Token, TokenType

TOKEN_REGEXES = {
    TokenType.CONSTANT: re.compile(r"[0-9]+\b"),
    TokenType.INT_KEYWORD: re.compile(r"int\b"),
    TokenType.VOID_KEYWORD: re.compile(r"void\b"),
    TokenType.RETURN: re.compile(r"return\b"),
    TokenType.L_PAREN: re.compile(r"\("),
    TokenType.R_PAREN: re.compile(r"\)"),
    TokenType.L_BRACE: re.compile(r"{"),
    TokenType.R_BRACE: re.compile(r"}"),
    TokenType.SEMICOLON: re.compile(r";"),
    TokenType.IDENTIFIER: re.compile(r"[a-zA-Z]\w*\b"),
    TokenType.COMPLEMENT: re.compile(r"~"),
    TokenType.DECREMENT: re.compile(r"--"),
    TokenType.NEGATION: re.compile(r"-"),
}


def lex(prog: str) -> List[Token]:
    tokens = []
    while prog:
        prog = prog.lstrip()
        match_found = False
        longest_match = 0
        matched_type = None
        matched_value = None
        for token_type, token_regex in TOKEN_REGEXES.items():
            match = token_regex.match(prog)
            if match:
                end = match.end()
                if end > longest_match:
                    match_found = True
                    longest_match = end
                    matched_type = token_type
                    matched_value = match.group()
        if match_found:
            tokens.append(Token(matched_type, matched_value))
            prog = prog[longest_match:]
        else:
            raise ValueError(f"Unexpected Token starting at:\n{prog}")
    return tokens
