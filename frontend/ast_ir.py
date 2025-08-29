from __future__ import annotations

from typing import Literal, NamedTuple


class Constant(NamedTuple):
    val: int


class Identifier(NamedTuple):
    name: str


class Return(NamedTuple):
    return_val: Expression


class Function(NamedTuple):
    name: Identifier
    body: Return


class Program(NamedTuple):
    function_definition: Function


class Complement(NamedTuple):
    operator: Literal["~"]


class Negation(NamedTuple):
    operator: Literal["-"]


class Add(NamedTuple):
    operator: Literal["+"]


class Subtract(NamedTuple):
    operator: Literal["-"]


class Multiply(NamedTuple):
    operator: Literal["*"]


class Divide(NamedTuple):
    operator: Literal["/"]


class Remainder(NamedTuple):
    operator: Literal["%"]


class UnaryOp(NamedTuple):
    operator: Complement | Negation
    inner_exp: Expression


class BinaryOp(NamedTuple):
    operator: Add | Subtract | Multiply | Divide | Remainder
    l_exp: Expression
    r_exp: Expression


Expression = Constant | UnaryOp | BinaryOp
