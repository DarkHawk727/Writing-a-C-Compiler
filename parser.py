import re
from typing import List, NamedTuple

from lexer import TOKEN_REGEXES
from tokens import Token, TokenType

Constant = NamedTuple("Constant", [("val", int)])
Identifier = NamedTuple("Identifier", [("name", str)])
Return = NamedTuple("Return", [("return_val", Constant)])
Function = NamedTuple("Function", [("name", Identifier), ("body", Return)])
Program = NamedTuple("Program", [("function_definition", Function)])


# This will remove the first element of tokens and pops it off. Modifies tokens
def expect(expected_type: TokenType, tokens: List[Token]) -> Token:
    if not tokens:
        raise SyntaxError("Unexpected end of input")
    tok = tokens.pop(0)
    if expected_type != tok.type:
        raise SyntaxError(f"Syntax Error: Expected {expected_type}, got {tok}")
    return tok


def parse_exp(tokens: List[Token]) -> Constant:
    # <exp> ::= <int>
    if not tokens:
        raise SyntaxError("Unexpected end of input.")

    tok = tokens.pop(0)

    if tok.type != TokenType.CONSTANT:
        raise SyntaxError(f"Expected constant, got {tok}")

    return Constant(int(tok.value))


def parse_statement(tokens: List[Token]) -> Return:
    # <statement> ::= "return" <constant> ";"
    if not tokens:
        raise SyntaxError("Unexpected end of input.")

    expect(TokenType.RETURN, tokens)
    return_val = parse_exp(tokens)
    expect(TokenType.SEMICOLON, tokens)

    return Return(return_val)


def parse_identifier(tokens: List[Token]) -> Identifier:
    # <identifier> ::= ? An identifier token ?
    if not tokens:
        raise SyntaxError("Unexpected end of input.")

    tok = tokens.pop(0)

    if tok.type != TokenType.IDENTIFIER:
        raise SyntaxError(f"Expected identifier, got {tok}")

    return Identifier(tok.value)


def parse_function(tokens: List[Token]) -> Function:
    # <function> ::= "int" <identifier> "(" "void" ")" "{" <statement> "}"
    if not tokens:
        raise SyntaxError("Unexpected enf of input.")

    expect(TokenType.INT_KEYWORD, tokens)
    identifier = parse_identifier(tokens)
    expect(TokenType.L_PAREN, tokens)
    expect(TokenType.VOID_KEYWORD, tokens)
    expect(TokenType.R_PAREN, tokens)
    expect(TokenType.L_BRACE, tokens)
    statement = parse_statement(tokens)
    expect(TokenType.R_BRACE, tokens)

    return Function(name=identifier, body=statement)


def parse_program(tokens: List[Token]) -> Program:
    # <program> ::= <function>
    main = parse_function(tokens)

    if tokens:
        raise SyntaxError(f"Unexpected tokens at end of program: {tokens}")

    return Program(main)
