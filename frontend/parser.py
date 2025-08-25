from __future__ import annotations

from typing import List

from frontend.ast_ir import *
from frontend.tokens import Token, TokenType


# This will remove the first element of tokens and pops it off. Modifies tokens
def _expect(expected_type: TokenType, tokens: List[Token]) -> Token:
    if not tokens:
        raise SyntaxError("Unexpected end of input")

    tok = tokens.pop(0)

    if expected_type != tok.type:
        raise SyntaxError(f"Syntax Error: Expected {expected_type}, got {tok}")
    return tok


def _parse_uop(tokens: List[Token]) -> Complement | Negation:
    if not tokens:
        raise SyntaxError("Unexpected end of input.")

    tok = tokens.pop(0)

    if tok.type == TokenType.COMPLEMENT:
        return Complement("~")
    elif tok.type == TokenType.NEGATION:
        return Negation("-")
    else:
        raise SyntaxError(f"Malformed expression, got {tok}")


def _parse_exp(tokens: List[Token]) -> Expression:
    # <exp> ::= <int> | <uop> <exp> | "(" <exp> ")"
    if not tokens:
        raise SyntaxError("Unexpected end of input.")

    tok = tokens[0]  ## Peek

    if tok.type == TokenType.CONSTANT:
        tokens.pop(0)
        return Constant(int(tok.value))
    elif tok.type == TokenType.COMPLEMENT or tok.type == TokenType.NEGATION:
        operator = _parse_uop(tokens)
        inner_exp = _parse_exp(tokens)
        return UnaryOp(operator, inner_exp)
    elif tok.type == TokenType.L_PAREN:
        tokens.pop(0)
        inner_exp = _parse_exp(tokens)
        _expect(TokenType.R_PAREN, tokens)
        return inner_exp
    else:
        raise SyntaxError(f"Malformed expression, got {tok}")


def _parse_statement(tokens: List[Token]) -> Return:
    # <statement> ::= "return" <constant> ";"
    if not tokens:
        raise SyntaxError("Unexpected end of input.")

    _expect(TokenType.RETURN, tokens)
    return_val = _parse_exp(tokens)
    _expect(TokenType.SEMICOLON, tokens)

    return Return(return_val)


def _parse_identifier(tokens: List[Token]) -> Identifier:
    # <identifier> ::= ? An identifier token ?
    if not tokens:
        raise SyntaxError("Unexpected end of input.")

    tok = tokens.pop(0)

    if tok.type != TokenType.IDENTIFIER:
        raise SyntaxError(f"Expected identifier, got {tok}")

    return Identifier(tok.value)


def _parse_function(tokens: List[Token]) -> Function:
    # <function> ::= "int" <identifier> "(" "void" ")" "{" <statement> "}"
    if not tokens:
        raise SyntaxError("Unexpected enf of input.")

    _expect(TokenType.INT_KEYWORD, tokens)
    identifier = _parse_identifier(tokens)
    _expect(TokenType.L_PAREN, tokens)
    _expect(TokenType.VOID_KEYWORD, tokens)
    _expect(TokenType.R_PAREN, tokens)
    _expect(TokenType.L_BRACE, tokens)
    statement = _parse_statement(tokens)
    _expect(TokenType.R_BRACE, tokens)

    return Function(name=identifier, body=statement)


def parse_program(tokens: List[Token]) -> Program:
    # <program> ::= <function>
    main = _parse_function(tokens)

    if tokens:
        raise SyntaxError(f"Unexpected tokens at end of program: {tokens}")

    return Program(main)
