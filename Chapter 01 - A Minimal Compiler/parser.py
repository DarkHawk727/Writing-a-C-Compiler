import re
from collections import namedtuple
from typing import List

TOKEN_REGEXES = {
    "IDENTIFIER": re.compile(r"[a-zA-Z]\w*\b"),  # IDENTIFIER
    "CONSTANT": re.compile(r"[0-9]+\b"),  # CONSTANT
    "INT_KEYWORD": re.compile(r"int\b"),  # INTEGER
    "VOID_KEYWORD": re.compile(r"void\b"),  # VOID
    "RETURN": re.compile(r"return\b"),  # RETURN
    "L_PAREN": re.compile(r"\("),  # L_PAREN
    "R_PAREN": re.compile(r"\)"),  # R_PAREN
    "L_BRACE": re.compile(r"{"),  # L_BRACE
    "R_BRACE": re.compile(r"}"),  # R_BRACE
    "SEMICOLON": re.compile(r";"),  # SEMICOLON
}

Program = namedtuple("Program", "main_func")
Function = namedtuple("Function", ["name", "body"])
Return = namedtuple("Return", "return_val")
Constant = namedtuple("Constant", "val")
Identifier = namedtuple("Identifier", "name")


def create_pretty_tuple_str(obj, indent=0) -> str:
    if not isinstance(obj, tuple):
        return str(obj)

    result = f"{type(obj).__name__}(\n"
    for field in obj._fields:
        value = getattr(obj, field)
        result += f"{' ' * (indent + 2)}{field}="
        result += create_pretty_tuple_str(value, indent + 2)
        result += ",\n"
    result += f"{' ' * indent})"
    return result


# This will remove the first element of tokens and pops it off. Modifies tokens
def expect(pattern: re.Pattern, tokens: List[str]) -> str:
    if not tokens:
        raise SyntaxError("Unexpected end of input")
    expected = tokens.pop(0)
    if not pattern.match(expected):
        raise SyntaxError(f"Syntax Error: Expected {pattern.pattern}, got {expected}")
    return expected


def parse_exp(tokens: List[str]) -> Constant:
    # <exp> ::= <int>
    if not tokens:
        raise SyntaxError("Unexpected end of input.")

    val = tokens.pop(0)

    if not TOKEN_REGEXES["CONSTANT"].match(val):
        raise SyntaxError(f"Expected constant, got {val}")

    return Constant(int(val))


def parse_statement(tokens: List[str]) -> Return:
    # <statement> ::= "return" <constant> ";"
    if not tokens:
        raise SyntaxError("Unexpected end of input.")

    expect(TOKEN_REGEXES["RETURN"], tokens)
    return_val = parse_exp(tokens)
    expect(TOKEN_REGEXES["SEMICOLON"], tokens)

    return Return(return_val)


def parse_identifier(tokens: List[str]) -> Identifier:
    # <identifier> ::= ? An identifier token ?
    if not tokens:
        raise SyntaxError("Unexpected end of input.")

    identifier_name = tokens.pop(0)

    if not TOKEN_REGEXES["IDENTIFIER"].match(identifier_name):
        raise SyntaxError(f"Expected identifier, got {identifier_name}")

    return Identifier(identifier_name)


def parse_function(tokens: List[str]) -> Function:
    # <function> ::= "int" <identifier> "(" "void" ")" "{" <statement> "}"
    if not tokens:
        raise SyntaxError("Unexpected enf of input.")

    expect(TOKEN_REGEXES["INT_KEYWORD"], tokens)
    identifier = parse_identifier(tokens)
    expect(TOKEN_REGEXES["L_PAREN"], tokens)
    expect(TOKEN_REGEXES["VOID_KEYWORD"], tokens)
    expect(TOKEN_REGEXES["R_PAREN"], tokens)
    expect(TOKEN_REGEXES["L_BRACE"], tokens)
    statement = parse_statement(tokens)
    expect(TOKEN_REGEXES["R_BRACE"], tokens)

    return Function(name=identifier, body=statement)


def parse_program(tokens: List[str]) -> Program:
    # <program> ::= <function>
    main = parse_function(tokens)

    if tokens:
        raise SyntaxError(f"Unexpected tokens at end of program: {tokens}")

    return Program(main)
