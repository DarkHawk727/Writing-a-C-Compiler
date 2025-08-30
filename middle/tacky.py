from itertools import count
from typing import Any, Dict, List

from frontend.ast_ir import (
    BinaryOp,
    BinaryOpType,
    Constant,
    Function,
    Program,
    UnaryOp,
    UnaryOpType,
)
from middle.tacky_ir import (
    TACKYBinaryOp,
    TACKYBinaryOpType,
    TACKYConstant,
    TACKYFunction,
    TACKYInstruction,
    TACKYProgram,
    TACKYReturn,
    TACKYUnaryOp,
    TACKYUnaryOpType,
    TACKYValue,
    TACKYVariable,
)

_temp_counter = count(0)


def make_temp():
    return f"tmp_{next(_temp_counter)}"


def _convert_uop(op: UnaryOpType) -> TACKYUnaryOpType:
    _UNARY_OP_MAP: Dict[UnaryOpType, TACKYUnaryOpType] = {
        UnaryOpType.COMPLEMENT: TACKYUnaryOpType.COMPLEMENT,
        UnaryOpType.NEGATION: TACKYUnaryOpType.NEGATION,
    }

    try:
        tacky_op = _UNARY_OP_MAP[op]
    except KeyError:
        raise TypeError(f"Unsupported binary operator: {op!r}")
    return tacky_op


def _convert_binaryop(op: BinaryOpType) -> TACKYBinaryOpType:
    _BINARY_OP_MAP: Dict[BinaryOpType, TACKYBinaryOpType] = {
        BinaryOpType.ADD: TACKYBinaryOpType.ADD,
        BinaryOpType.SUBTRACT: TACKYBinaryOpType.SUBTRACT,
        BinaryOpType.MULTIPLY: TACKYBinaryOpType.MULTIPLY,
        BinaryOpType.DIVIDE: TACKYBinaryOpType.DIVIDE,
        BinaryOpType.REMAINDER: TACKYBinaryOpType.REMAINDER,
        BinaryOpType.BITWISE_AND: TACKYBinaryOpType.BITWISE_AND,
        BinaryOpType.BITWISE_OR: TACKYBinaryOpType.BITWISE_OR,
        BinaryOpType.BITWISE_XOR: TACKYBinaryOpType.BITWISE_XOR,
        BinaryOpType.L_SHIFT: TACKYBinaryOpType.L_SHIFT,
        BinaryOpType.R_SHIFT: TACKYBinaryOpType.R_SHIFT,
    }

    try:
        tacky_op = _BINARY_OP_MAP[op]
    except KeyError:
        raise TypeError(f"Unsupported binary operator: {op!r}")
    return tacky_op


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
