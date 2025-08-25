from itertools import count
from typing import Any, List

from frontend.parser import Complement, Constant, Function, Negation, Program, UnaryOp
from middle.tacky_ir import *

_temp_counter = count(0)


def make_temp():
    return f"tmp_{next(_temp_counter)}"


def convert_unop(op):
    if isinstance(op, Complement):
        return Complement("~")
    elif isinstance(op, Negation):
        return Negation("-")
    else:
        raise ValueError(f"Unknown unary operator: {op}")


def emit_TACKY(expr: Any, instructions: List) -> TACKYValue:
    match expr:
        case Constant(val):
            return TACKYConstant(val)

        case UnaryOp(op, inner_expr):
            src = emit_TACKY(inner_expr, instructions)
            dst_name = make_temp()
            dst = TACKYVariable(dst_name)
            tacky_op = convert_unop(op)
            instructions.append(TACKYUnaryOp(tacky_op, src, dst))
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
