from typing import List, TypeAlias, cast

from backend.assembly_ir import (
    AssemblyAllocateStack,
    AssemblyComplement,
    AssemblyFunction,
    AssemblyImmediate,
    AssemblyMov,
    AssemblyNegation,
    AssemblyProgram,
    AssemblyPseudoRegister,
    AssemblyRegister,
    AssemblyRet,
    AssemblyStack,
    AssemblyUnary,
    OffsetAllocator,
)
from middle.tacky_ir import (
    TACKYConstant,
    TACKYFunction,
    TACKYInstruction,
    TACKYProgram,
    TACKYReturn,
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

    if hasattr(node.unary_operator, "operator") and node.unary_operator.operator == "~":
        u = AssemblyUnary(AssemblyComplement(), dst)
    elif (
        hasattr(node.unary_operator, "operator") and node.unary_operator.operator == "-"
    ):
        u = AssemblyUnary(AssemblyNegation(), dst)
    else:
        try:
            from frontend.parser import Complement, Negation  # type: ignore

            if isinstance(node.unary_operator, Complement):
                u = AssemblyUnary(AssemblyComplement(), dst)
            elif isinstance(node.unary_operator, Negation):
                u = AssemblyUnary(AssemblyNegation(), dst)
            else:
                raise TypeError
        except Exception:
            raise TypeError(f"Unsupported unary operator: {node.unary_operator!r}")

    return [mov, u]


def _visit_return(tacky_return: TACKYReturn) -> List[AssemblyMov | AssemblyRet]:
    return [
        AssemblyMov(_visit_value(tacky_return.value), AssemblyRegister("AX")),
        AssemblyRet(),
    ]


def _visit_instr(tacky_instr: TACKYInstruction) -> List:
    if isinstance(tacky_instr, TACKYUnaryOp):
        return _visit_unary(tacky_instr)
    elif isinstance(tacky_instr, TACKYReturn):
        return _visit_return(tacky_instr)
    else:
        raise NotImplementedError(f"No visit logic for {type(tacky_instr).__name__}")


def visit_function(tacky_func: TACKYFunction) -> AssemblyFunction:
    instructions: List = []
    oa = OffsetAllocator()
    for instr in tacky_func.instructions:
        instructions.extend(_visit_instr(instr))

    return AssemblyFunction(tacky_func.identifier, instructions, oa)


def visit_program(tacky_prog: TACKYProgram) -> AssemblyProgram:
    func = visit_function(tacky_prog.function_definition)
    func = replace_pseudoregisters(func)
    func = instruction_fixup(func)
    return AssemblyProgram(func)


SrcOperand: TypeAlias = "AssemblyImmediate | AssemblyRegister | AssemblyStack"
DstOperand: TypeAlias = "AssemblyRegister | AssemblyStack"


def replace_pseudoregisters(assembly_func: AssemblyFunction) -> AssemblyFunction:
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

            case _:
                continue

    return assembly_func


def instruction_fixup(assembly_func: AssemblyFunction) -> AssemblyFunction:
    instrs: List[AssemblyMov | AssemblyUnary | AssemblyRet | AssemblyAllocateStack] = [
        AssemblyAllocateStack(assembly_func.offsets.max_offset)
    ]
    for instruction in assembly_func.instructions:
        match instruction:
            case AssemblyMov(AssemblyStack(src_offset), AssemblyStack(dst_offset)):
                instrs.append(
                    AssemblyMov(AssemblyStack(src_offset), AssemblyRegister("R10"))
                )
                instrs.append(
                    AssemblyMov(AssemblyRegister("R10"), AssemblyStack(dst_offset))
                )

            case _:
                instrs.append(instruction)
    return AssemblyFunction(assembly_func.name, instrs, assembly_func.offsets)


def convert_TACKY_to_assembly(tacky_prog: TACKYProgram) -> AssemblyProgram:
    return visit_program(tacky_prog)
