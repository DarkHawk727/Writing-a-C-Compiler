from __future__ import annotations

from typing import List, Literal, NamedTuple, Union


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


class UnaryOp(NamedTuple):
    operator: Union[Complement, Negation]
    inner_exp: Expression


Expression = Union[Constant, UnaryOp]
