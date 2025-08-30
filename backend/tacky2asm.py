from typing import Any, List, TypeAlias, cast

from backend.assembly_ir import (
    AssemblyAllocateStack,
    AssemblyBinaryOp,
    AssemblyBinaryOpType,
    AssemblyCdq,
    AssemblyFunction,
    AssemblyIDiv,
    AssemblyImmediate,
    AssemblyMov,
    AssemblyPop,
    AssemblyProgram,
    AssemblyPseudoRegister,
    AssemblyRegister,
    AssemblyRet,
    AssemblyStack,
    AssemblyUnary,
    AssemblyUnaryOpType,
    OffsetAllocator,
    Operand,
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


def _visit_value(tacky_value: TACKYValue) -> AssemblyImmediate | AssemblyPseudoRegister:
    if isinstance(tacky_value, TACKYConstant):
        return AssemblyImmediate(tacky_value.value)
    elif isinstance(tacky_value, TACKYVariable):
        return AssemblyPseudoRegister(tacky_value.identifier)
    raise TypeError(f"Unsupported TACKY value: {type(tacky_value).__name__}")


def _visit_unary(node: TACKYUnaryOp) -> List[AssemblyMov | AssemblyUnary]:
    dst = AssemblyPseudoRegister(node.destination.identifier)
    mov = AssemblyMov(_visit_value(node.source), dst)

    match node.unary_operator:
        case TACKYUnaryOpType.COMPLEMENT:
            u = AssemblyUnary(AssemblyUnaryOpType.COMPLEMENT, dst)

        case TACKYUnaryOpType.NEGATION:
            u = AssemblyUnary(AssemblyUnaryOpType.NEGATION, dst)

        case _:
            raise TypeError(f"Unsupported unary operator: {node.unary_operator!r}")

    return [mov, u]


def _visit_binary(
    node: TACKYBinaryOp,
) -> List[AssemblyMov | AssemblyBinaryOp | AssemblyCdq | AssemblyIDiv]:
    instrs: List[AssemblyMov | AssemblyBinaryOp | AssemblyCdq | AssemblyIDiv] = []

    dst = AssemblyPseudoRegister(node.destination.identifier)
    match node.binary_operator:
        case TACKYBinaryOpType.ADD:
            instrs.extend(
                [
                    AssemblyMov(
                        _visit_value(node.source_1),
                        dst,
                    ),
                    AssemblyBinaryOp(
                        AssemblyBinaryOpType.ADD, _visit_value(node.source_2), dst
                    ),
                ]
            )

        case TACKYBinaryOpType.SUBTRACT:
            instrs.extend(
                [
                    AssemblyMov(
                        _visit_value(node.source_1),
                        dst,
                    ),
                    AssemblyBinaryOp(
                        AssemblyBinaryOpType.SUBTRACT, _visit_value(node.source_2), dst
                    ),
                ]
            )

        case TACKYBinaryOpType.MULTIPLY:
            instrs.extend(
                [
                    AssemblyMov(
                        _visit_value(node.source_1),
                        dst,
                    ),
                    AssemblyBinaryOp(
                        AssemblyBinaryOpType.MULTIPLY, _visit_value(node.source_2), dst
                    ),
                ]
            )

        case TACKYBinaryOpType.DIVIDE:
            instrs.extend(
                [
                    AssemblyMov(_visit_value(node.source_1), AssemblyRegister("AX")),
                    AssemblyCdq(),
                    AssemblyIDiv(_visit_value(node.source_2)),
                    AssemblyMov(AssemblyRegister("AX"), dst),
                ]
            )

        case TACKYBinaryOpType.REMAINDER:
            instrs.extend(
                [
                    AssemblyMov(_visit_value(node.source_1), AssemblyRegister("AX")),
                    AssemblyCdq(),
                    AssemblyIDiv(_visit_value(node.source_2)),
                    AssemblyMov(AssemblyRegister("DX"), dst),
                ]
            )

        case TACKYBinaryOpType.BITWISE_AND:
            instrs.extend(
                [
                    AssemblyMov(
                        _visit_value(node.source_1),
                        dst,
                    ),
                    AssemblyBinaryOp(
                        AssemblyBinaryOpType.BITWISE_AND,
                        _visit_value(node.source_2),
                        dst,
                    ),
                ]
            )

        case TACKYBinaryOpType.BITWISE_OR:
            instrs.extend(
                [
                    AssemblyMov(
                        _visit_value(node.source_1),
                        dst,
                    ),
                    AssemblyBinaryOp(
                        AssemblyBinaryOpType.BITWISE_OR,
                        _visit_value(node.source_2),
                        dst,
                    ),
                ]
            )

        case TACKYBinaryOpType.BITWISE_XOR:
            instrs.extend(
                [
                    AssemblyMov(
                        _visit_value(node.source_1),
                        dst,
                    ),
                    AssemblyBinaryOp(
                        AssemblyBinaryOpType.BITWISE_XOR,
                        _visit_value(node.source_2),
                        dst,
                    ),
                ]
            )

        case TACKYBinaryOpType.L_SHIFT:
            instrs.extend(
                [
                    AssemblyMov(
                        _visit_value(node.source_1),
                        dst,
                    ),
                    AssemblyBinaryOp(
                        AssemblyBinaryOpType.L_SHIFT, _visit_value(node.source_2), dst
                    ),
                ]
            )

        case TACKYBinaryOpType.R_SHIFT:
            instrs.extend(
                [
                    AssemblyMov(
                        _visit_value(node.source_1),
                        dst,
                    ),
                    AssemblyBinaryOp(
                        AssemblyBinaryOpType.R_SHIFT, _visit_value(node.source_2), dst
                    ),
                ]
            )

        case _:
            raise NotImplementedError(
                f"No visit logic for {type(node.binary_operator).__name__}"
            )

    return instrs


def _visit_return(tacky_return: TACKYReturn) -> List[AssemblyMov | AssemblyRet]:
    return [
        AssemblyMov(_visit_value(tacky_return.value), AssemblyRegister("AX")),
        AssemblyRet(),
    ]


def _visit_instruction(tacky_instr: TACKYInstruction) -> List:
    if isinstance(tacky_instr, TACKYUnaryOp):
        return _visit_unary(tacky_instr)
    elif isinstance(tacky_instr, TACKYReturn):
        return _visit_return(tacky_instr)
    elif isinstance(tacky_instr, TACKYBinaryOp):
        return _visit_binary(tacky_instr)
    else:
        raise NotImplementedError(f"No visit logic for {type(tacky_instr).__name__}")


def _visit_function(tacky_func: TACKYFunction) -> AssemblyFunction:
    instructions: List = []
    oa = OffsetAllocator()
    for instr in tacky_func.instructions:
        instructions.extend(_visit_instruction(instr))

    return AssemblyFunction(tacky_func.identifier, instructions, oa)


def _visit_program(tacky_prog: TACKYProgram) -> AssemblyProgram:
    func = _visit_function(tacky_prog.function_definition)
    func = _replace_pseudoregisters(func)
    func = _instruction_fixup(func)
    return AssemblyProgram(func)


SrcOperand: TypeAlias = "AssemblyImmediate | AssemblyRegister | AssemblyStack"
DstOperand: TypeAlias = "AssemblyRegister | AssemblyStack"


def _stackify(operand: Operand, offsets: OffsetAllocator) -> Operand:
    if isinstance(operand, AssemblyPseudoRegister):
        return AssemblyStack(offsets[operand.identifier])
    return operand


def _replace_pseudoregisters(assembly_func: AssemblyFunction) -> AssemblyFunction:
    for i, instruction in enumerate(assembly_func.instructions):
        match instruction:
            case AssemblyMov(e, r):
                assembly_func.instructions[i] = AssemblyMov(
                    _stackify(e, assembly_func.offsets),
                    _stackify(r, assembly_func.offsets),
                )

            case AssemblyUnary(op, o):
                if isinstance(o, AssemblyPseudoRegister):
                    assembly_func.instructions[i] = AssemblyUnary(
                        op, _stackify(o, assembly_func.offsets)
                    )

            case AssemblyBinaryOp(op, o1, o2):
                assembly_func.instructions[i] = AssemblyBinaryOp(
                    op,
                    _stackify(o1, assembly_func.offsets),
                    _stackify(o2, assembly_func.offsets),
                )

            case AssemblyIDiv(o1):
                if isinstance(o1, AssemblyPseudoRegister):
                    assembly_func.instructions[i] = AssemblyIDiv(
                        _stackify(o1, assembly_func.offsets)
                    )

            case _:
                continue

    return assembly_func


def _is_mem(x: Operand) -> bool:
    return isinstance(x, AssemblyStack)


def _is_imm(x: Operand) -> bool:
    return isinstance(x, AssemblyImmediate)


def _instruction_fixup(assembly_func: AssemblyFunction) -> AssemblyFunction:
    frame_size = ((assembly_func.offsets.max_offset + 15) // 16) * 16 # Need to keep the stack frame a multiple of 16
    instrs: List[Any] = [AssemblyAllocateStack(frame_size)]

    for ins in assembly_func.instructions:
        match ins:

            case AssemblyMov(AssemblyStack(src_off), AssemblyStack(dst_off)):
                instrs.append(
                    AssemblyMov(AssemblyStack(src_off), AssemblyRegister("R10"))
                )
                instrs.append(
                    AssemblyMov(AssemblyRegister("R10"), AssemblyStack(dst_off))
                )

            case AssemblyIDiv(op) if _is_imm(op):
                instrs.append(
                    AssemblyMov(cast(AssemblyImmediate, op), AssemblyRegister("R10"))
                )
                instrs.append(AssemblyIDiv(AssemblyRegister("R10")))

            case AssemblyBinaryOp(op, src, dst):
                if op == AssemblyBinaryOpType.MULTIPLY:
                    if _is_mem(dst):
                        dst_off = cast(AssemblyStack, dst).offset
                        instrs.append(
                            AssemblyMov(AssemblyStack(dst_off), AssemblyRegister("R11"))
                        )

                        fixed_src: Operand
                        if _is_mem(src):
                            instrs.append(
                                AssemblyMov(
                                    cast(AssemblyStack, src), AssemblyRegister("R10")
                                )
                            )
                            fixed_src = AssemblyRegister("R10")
                        else:
                            fixed_src = src

                        instrs.append(
                            AssemblyBinaryOp(
                                AssemblyBinaryOpType.MULTIPLY,
                                fixed_src,
                                AssemblyRegister("R11"),
                            )
                        )
                        instrs.append(
                            AssemblyMov(AssemblyRegister("R11"), AssemblyStack(dst_off))
                        )

                    else:
                        if _is_mem(src) and _is_mem(dst):
                            instrs.append(
                                AssemblyMov(
                                    cast(AssemblyStack, src), AssemblyRegister("R10")
                                )
                            )
                            instrs.append(
                                AssemblyBinaryOp(
                                    AssemblyBinaryOpType.MULTIPLY,
                                    AssemblyRegister("R10"),
                                    dst,
                                )
                            )
                        else:
                            instrs.append(ins)

                elif (
                    op == AssemblyBinaryOpType.ADD
                    or op == AssemblyBinaryOpType.SUBTRACT
                ):
                    if _is_mem(src) and _is_mem(dst):
                        instrs.append(
                            AssemblyMov(
                                cast(AssemblyStack, src), AssemblyRegister("R10")
                            )
                        )
                        instrs.append(
                            AssemblyBinaryOp(op, AssemblyRegister("R10"), dst)
                        )
                    else:
                        instrs.append(ins)

                else:
                    if _is_mem(src) and _is_mem(dst):
                        instrs.append(
                            AssemblyMov(
                                cast(AssemblyStack, src), AssemblyRegister("R10")
                            )
                        )
                        instrs.append(
                            AssemblyBinaryOp(op, AssemblyRegister("R10"), dst)
                        )
                    else:
                        instrs.append(ins)

            case _:
                instrs.append(ins)

    return AssemblyFunction(assembly_func.name, instrs, assembly_func.offsets)


def convert_TACKY_to_assembly(tacky_prog: TACKYProgram) -> AssemblyProgram:
    return _visit_program(tacky_prog)
