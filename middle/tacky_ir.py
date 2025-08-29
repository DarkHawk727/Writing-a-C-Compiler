from __future__ import annotations

from typing import List, Literal, NamedTuple, TypeAlias


class TACKYConstant(NamedTuple):
    value: int


class TACKYVariable(NamedTuple):
    identifier: str


TACKYValue: TypeAlias = TACKYConstant | TACKYVariable


class TACKYComplement(NamedTuple):
    op: Literal["~"]


class TACKYNegation(NamedTuple):
    op: Literal["-"]


class TACKYAdd(NamedTuple):
    op: Literal["+"]


class TACKYSubtract(NamedTuple):
    op: Literal["-"]


class TACKYMultiply(NamedTuple):
    op: Literal["*"]


class TACKYDivide(NamedTuple):
    op: Literal["/"]


class TACKYRemainder(NamedTuple):
    op: Literal["%"]


class TACKYUnaryOp(NamedTuple):
    unary_operator: TACKYComplement | TACKYNegation
    source: TACKYValue
    destination: TACKYValue


class TACKYBinaryOp(NamedTuple):
    binary_operator: (
        TACKYAdd | TACKYSubtract | TACKYMultiply | TACKYDivide | TACKYRemainder
    )
    source_1: TACKYValue
    source_2: TACKYValue
    destination: TACKYValue


class TACKYReturn(NamedTuple):
    value: TACKYValue


TACKYInstruction: TypeAlias = TACKYReturn | TACKYUnaryOp


class TACKYFunction(NamedTuple):
    identifier: str
    instructions: List[TACKYInstruction]


class TACKYProgram(NamedTuple):
    function_definition: TACKYFunction
