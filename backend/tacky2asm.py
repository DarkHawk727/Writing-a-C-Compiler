from typing import Any, List, TypeAlias, cast

from backend.assembly_ir import (
    AssemblyAdd,
    AssemblyAllocateStack,
    AssemblyBinaryOp,
    AssemblyCdq,
    AssemblyComplement,
    AssemblyFunction,
    AssemblyIDiv,
    AssemblyImmediate,
    AssemblyMov,
    AssemblyMultiply,
    AssemblyNegation,
    AssemblyPop,
    AssemblyProgram,
    AssemblyPseudoRegister,
    AssemblyRegister,
    AssemblyRet,
    AssemblyStack,
    AssemblySubtract,
    AssemblyUnary,
    OffsetAllocator,
    Operand,
)
from middle.tacky_ir import (
    TACKYAdd,
    TACKYBinaryOp,
    TACKYComplement,
    TACKYConstant,
    TACKYDivide,
    TACKYFunction,
    TACKYInstruction,
    TACKYMultiply,
    TACKYNegation,
    TACKYProgram,
    TACKYRemainder,
    TACKYReturn,
    TACKYSubtract,
    TACKYUnaryOp,
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
        case TACKYComplement():
            u = AssemblyUnary(AssemblyComplement(), dst)

        case TACKYNegation():
            u = AssemblyUnary(AssemblyNegation(), dst)

        case _:
            raise TypeError(f"Unsupported unary operator: {node.unary_operator!r}")

    return [mov, u]


def _visit_binary(
    node: TACKYBinaryOp,
) -> List[AssemblyMov | AssemblyBinaryOp | AssemblyCdq | AssemblyIDiv]:
    instrs: List[AssemblyMov | AssemblyBinaryOp | AssemblyCdq | AssemblyIDiv] = []

    dst = AssemblyPseudoRegister(node.destination.identifier)
    match node.binary_operator:
        case TACKYAdd():
            instrs.extend(
                [
                    AssemblyMov(
                        _visit_value(node.source_1),
                        dst,
                    ),
                    AssemblyBinaryOp(AssemblyAdd(), _visit_value(node.source_2), dst),
                ]
            )

        case TACKYSubtract():
            instrs.extend(
                [
                    AssemblyMov(
                        _visit_value(node.source_1),
                        dst,
                    ),
                    AssemblyBinaryOp(
                        AssemblySubtract(), _visit_value(node.source_2), dst
                    ),
                ]
            )

        case TACKYMultiply():
            instrs.extend(
                [
                    AssemblyMov(
                        _visit_value(node.source_1),
                        dst,
                    ),
                    AssemblyBinaryOp(
                        AssemblyMultiply(), _visit_value(node.source_2), dst
                    ),
                ]
            )

        case TACKYDivide():
            instrs.extend(
                [
                    AssemblyMov(_visit_value(node.source_1), AssemblyRegister("AX")),
                    AssemblyCdq(),
                    AssemblyIDiv(_visit_value(node.source_2)),
                    AssemblyMov(AssemblyRegister("AX"), dst),
                ]
            )

        case TACKYRemainder():
            instrs.extend(
                [
                    AssemblyMov(_visit_value(node.source_1), AssemblyRegister("AX")),
                    AssemblyCdq(),
                    AssemblyIDiv(_visit_value(node.source_2)),
                    AssemblyMov(AssemblyRegister("DX"), dst),
                ]
            )

        case _:
            raise TypeError(f"Unsupported binary operator: {node.binary_operator!r}")

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


def _replace_pseudoregisters(assembly_func: AssemblyFunction) -> AssemblyFunction:
    for i, instruction in enumerate(assembly_func.instructions):
        match instruction:
            case AssemblyMov(e, r):
                new_e: SrcOperand
                if isinstance(e, AssemblyPseudoRegister):
                    new_e = AssemblyStack(assembly_func.offsets[e.identifier])
                else:
                    new_e = cast(SrcOperand, e)

                new_r: DstOperand
                if isinstance(r, AssemblyPseudoRegister):
                    new_r = AssemblyStack(assembly_func.offsets[r.identifier])
                else:
                    new_r = cast(DstOperand, r)

                assembly_func.instructions[i] = AssemblyMov(new_e, new_r)

            case AssemblyUnary(op, o):
                if isinstance(o, AssemblyPseudoRegister):
                    assembly_func.instructions[i] = AssemblyUnary(
                        op, AssemblyStack(assembly_func.offsets[o.identifier])
                    )

            case AssemblyBinaryOp(op, o1, o2):
                if isinstance(o1, AssemblyPseudoRegister):
                    new_o1 = AssemblyStack(assembly_func.offsets[o1.identifier])
                else:
                    new_o1 = o1

                if isinstance(o2, AssemblyPseudoRegister):
                    new_o2 = AssemblyStack(assembly_func.offsets[o2.identifier])
                else:
                    new_o2 = o2

                assembly_func.instructions[i] = AssemblyBinaryOp(op, new_o1, new_o2)

            case AssemblyIDiv(o1):
                if isinstance(o1, AssemblyPseudoRegister):
                    assembly_func.instructions[i] = AssemblyIDiv(
                        AssemblyStack(assembly_func.offsets[o1.identifier])
                    )

            case _:
                continue

    return assembly_func


def _instruction_fixup(assembly_func: AssemblyFunction) -> AssemblyFunction:
    instrs: List[Any] = [AssemblyAllocateStack(assembly_func.offsets.max_offset)]
    for instruction in assembly_func.instructions:
        match instruction:
            case AssemblyMov(AssemblyStack(src_offset), AssemblyStack(dst_offset)):
                instrs.append(
                    AssemblyMov(AssemblyStack(src_offset), AssemblyRegister("R10"))
                )
                instrs.append(
                    AssemblyMov(AssemblyRegister("R10"), AssemblyStack(dst_offset))
                )

            case AssemblyIDiv(AssemblyImmediate(v)):
                instrs.extend(
                    [
                        AssemblyMov(AssemblyImmediate(v), AssemblyRegister("R10")),
                        AssemblyIDiv(AssemblyRegister("R10")),
                    ]
                )

            case AssemblyBinaryOp(AssemblyAdd(), AssemblyStack(off_1), op_2):
                instrs.extend(
                    [
                        AssemblyMov(AssemblyStack(off_1), AssemblyRegister("R10")),
                        AssemblyBinaryOp(AssemblyAdd(), AssemblyRegister("R10"), op_2),
                    ]
                )

            case AssemblyBinaryOp(AssemblySubtract(), AssemblyStack(off_1), op_2):
                instrs.extend(
                    [
                        AssemblyMov(AssemblyStack(off_1), AssemblyRegister("R10")),
                        AssemblyBinaryOp(
                            AssemblySubtract(), AssemblyRegister("R10"), op_2
                        ),
                    ]
                )

            case AssemblyBinaryOp(
                AssemblyMultiply(), AssemblyImmediate(v), AssemblyStack(off)
            ):
                instrs.extend(
                    [
                        AssemblyMov(AssemblyStack(off), AssemblyRegister("R11")),
                        AssemblyBinaryOp(
                            AssemblyMultiply(),
                            AssemblyImmediate(v),
                            AssemblyRegister("R11"),
                        ),
                        AssemblyMov(AssemblyRegister("R11"), AssemblyStack(off)),
                    ]
                )

            case _:
                instrs.append(instruction)
    return AssemblyFunction(assembly_func.name, instrs, assembly_func.offsets)


def convert_TACKY_to_assembly(tacky_prog: TACKYProgram) -> AssemblyProgram:
    return _visit_program(tacky_prog)
