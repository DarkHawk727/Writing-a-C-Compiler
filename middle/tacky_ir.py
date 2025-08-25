from __future__ import annotations

from typing import List, NamedTuple, TypeAlias, Union

from frontend.parser import Complement, Negation


class TACKYConstant(NamedTuple):
    value: int


class TACKYVariable(NamedTuple):
    identifier: str


TACKYValue: TypeAlias = Union[TACKYConstant, TACKYVariable]


class TACKYUnaryOp(NamedTuple):
    unary_operator: Union[Complement, Negation]
    source: TACKYValue
    destination: TACKYVariable


class TACKYReturn(NamedTuple):
    value: TACKYValue


TACKYInstruction: TypeAlias = Union[TACKYReturn, TACKYUnaryOp]


class TACKYFunction(NamedTuple):
    identifier: str
    instructions: List[TACKYInstruction]


class TACKYProgram(NamedTuple):
    function_definition: TACKYFunction
