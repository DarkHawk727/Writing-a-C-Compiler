import re
from typing import List

TOKEN_REGEXES = [
    re.compile(r"[a-zA-Z]\w*\b"),  # IDENTIFIER
    re.compile(r"[0-9]+\b"),  # CONSTANT
    re.compile(r"int\b"),  # INTEGER
    re.compile(r"void\b"),  # VOID
    re.compile(r"return\b"),  # RETURN
    re.compile(r"\("),  # L_PAREN
    re.compile(r"\)"),  # R_PAREN
    re.compile(r"{"),  # L_BRACE
    re.compile(r"}"),  # R_BRACE
    re.compile(r";"),  # SEMICOLON
]


def lex(prog: str) -> List[str]:
    tokens = []
    while prog:
        match_found = False
        longest_match = 0
        if prog := prog.lstrip():
            for token_regex in TOKEN_REGEXES:
                if token := token_regex.match(prog):
                    end = token.end()
                    if end > longest_match:
                        match_found = True
                        longest_match = end
                        tokens.append(token.group())
                        prog = prog[end:]
            if not match_found:
                raise ValueError(f"Unexpected Token starting at:\n{prog}")
    return tokens
