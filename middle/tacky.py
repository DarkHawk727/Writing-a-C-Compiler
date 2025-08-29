from itertools import count
from typing import Any, List

from frontend.parser import (
    Add,
    BinaryOp,
    Complement,
    Constant,
    Divide,
    Function,
    Multiply,
    Negation,
    Program,
    Remainder,
    Subtract,
    UnaryOp,
)
from middle.tacky_ir import *

_temp_counter = count(0)


def make_temp():
    return f"tmp_{next(_temp_counter)}"


def _convert_uop(op: Complement | Negation) -> TACKYComplement | TACKYNegation:
    match op:
        case Complement():
            return TACKYComplement("~")

        case Negation():
            return TACKYNegation("-")

        case _:
            raise TypeError(f"Unsupported unary operator: {op.unary_operator!r}")


def _convert_binaryop(
    op: Add | Subtract | Multiply | Divide | Remainder,
) -> TACKYAdd | TACKYSubtract | TACKYMultiply | TACKYDivide | TACKYRemainder:
    match op:
        case Add():
            return TACKYAdd("+")

        case Subtract():
            return TACKYSubtract("-")

        case Multiply():
            return TACKYMultiply("*")

        case Divide():
            return TACKYDivide("/")

        case Remainder():
            return TACKYRemainder("%")

        case _:
            raise TypeError(f"Unsupported binary operator: {op!r}")


def emit_TACKY(expr: Any, instructions: List) -> TACKYValue:
    match expr:
        case Constant(val):
            return TACKYConstant(val)

        case UnaryOp(op, inner_expr):
            tacky_op = _convert_uop(op)
            src = emit_TACKY(inner_expr, instructions)
            dst_name = make_temp()
            dst = TACKYVariable(dst_name)
            instructions.append(TACKYUnaryOp(tacky_op, src, dst))
            return dst

        case BinaryOp(op, e1, e2):
            tacky_binop = _convert_binaryop(op)
            v1 = emit_TACKY(e1, instructions)
            v2 = emit_TACKY(e2, instructions)
            dst_name = make_temp()
            dst = TACKYVariable(dst_name)
            instructions.append(TACKYBinaryOp(tacky_binop, v1, v2, dst))
            return dst

        case _:
            raise NotImplementedError(f"emit_tacky: {type(expr).__name__}")


def convert_AST_to_TACKY(node: Any) -> Any:
    match node:
        case Program(main_func):
            func_def = convert_AST_to_TACKY(main_func)
            return TACKYProgram(func_def)

        case Function(n, b):
            instrs: List[TACKYInstruction] = []
            instrs.append(TACKYReturn(emit_TACKY(b.return_val, instrs)))
            return TACKYFunction(n.name, instrs)

        case _:
            raise NotImplementedError(f"convert_AST_to_TACKY: {type(node).__name__}")
