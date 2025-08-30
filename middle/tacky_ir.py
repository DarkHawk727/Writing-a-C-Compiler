from __future__ import annotations

from enum import Enum, auto
from typing import List, NamedTuple, TypeAlias


class TACKYConstant(NamedTuple):
    value: int


class TACKYVariable(NamedTuple):
    identifier: str


TACKYValue: TypeAlias = TACKYConstant | TACKYVariable


class TACKYUnaryOpType(Enum):
    COMPLEMENT = auto()
    NEGATION = auto()


class TACKYUnaryOp(NamedTuple):
    unary_operator: TACKYUnaryOpType
    source: TACKYValue
    destination: TACKYValue


class TACKYBinaryOpType(Enum):
    ADD = auto()
    SUBTRACT = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    REMAINDER = auto()
    BITWISE_AND = auto()
    BITWISE_OR = auto()
    BITWISE_XOR = auto()
    L_SHIFT = auto()
    R_SHIFT = auto()


class TACKYBinaryOp(NamedTuple):
    binary_operator: TACKYBinaryOpType
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
