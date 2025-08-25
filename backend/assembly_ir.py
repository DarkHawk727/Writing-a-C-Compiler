from __future__ import annotations

import itertools
from typing import Any, List, Literal, NamedTuple


class OffsetAllocator(dict):
    def __init__(self, start=-4, step=-4) -> None:
        super().__init__()
        self.counter = itertools.count(start, step)
        self.max_offset = start

    def __missing__(self, var_name: str) -> int:
        offset = next(self.counter)
        self[var_name] = offset
        self.max_offset = offset
        return offset



class AssemblyFunction(NamedTuple):
    name: str
    instructions: List[Any]
    offsets: OffsetAllocator


class AssemblyProgram(NamedTuple):
    function_definition: AssemblyFunction


class AssemblyImmediate(NamedTuple):
    value: int | str


class AssemblyMov(NamedTuple):
    exp: AssemblyRegister | AssemblyImmediate | AssemblyPseudoRegister | AssemblyStack
    register: AssemblyRegister | AssemblyPseudoRegister | AssemblyStack


class AssemblyPop(NamedTuple):
    register: str


class AssemblyRet(NamedTuple):
    pass


class AssemblyNegation(NamedTuple):
    pass


class AssemblyComplement(NamedTuple):
    pass


class AssemblyUnary(NamedTuple):
    unary_operator: AssemblyNegation | AssemblyComplement
    operand: Any


class AssemblyAllocateStack(NamedTuple):
    val: int


class AssemblyRegister(NamedTuple):
    reg: Literal["AX", "R10"]


class AssemblyStack(NamedTuple):
    offset: int


class AssemblyPseudoRegister(NamedTuple):
    identifier: str
