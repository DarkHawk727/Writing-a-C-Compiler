from typing import List

from backend.assembly_ir import (
    AssemblyAllocateStack,
    AssemblyComplement,
    AssemblyFunction,
    AssemblyImmediate,
    AssemblyMov,
    AssemblyNegation,
    AssemblyProgram,
    AssemblyRegister,
    AssemblyRet,
    AssemblyStack,
    AssemblyUnary,
)


def emit_assembly(node: AssemblyProgram | AssemblyFunction) -> List[str]:
    match node:
        case AssemblyProgram(func):
            return emit_assembly(func)

        case AssemblyFunction(name, instructions):
            lines = [f"\t.globl {name}", f"_{name}:", "\tpushq\t%rbp", "\tmovq\t%rsp, %rbp"]
            for instr in instructions:
                lines.extend(emit_assembly(instr))
            return lines

        case AssemblyMov(exp, register):
            return [f"\tmovl\t{emit_assembly(exp)[0]}, {emit_assembly(register)[0]}"]

        case AssemblyRet():
            return ["\tmovq\t%rbp, %rsp", "\tpopq\t%rbp", "\tret"]

        case AssemblyUnary(uop, operand):
            if isinstance(uop, AssemblyNegation):
                return [f"\tnegl\t{emit_assembly(operand)[0]}"]
            elif isinstance(uop, AssemblyComplement):
                return [f"\tnotl\t{emit_assembly(operand)[0]}"]

        case AssemblyAllocateStack(v):
            return [f"\tsubq\t${abs(v)}, %rsp"]

        case AssemblyRegister(reg):
            if reg == "AX":
                return ["%eax"]
            elif reg == "R10":
                return ["%r10d"]

        case AssemblyStack(offset):
            return [f"{offset}(%rbp)"]

        case AssemblyImmediate(val):
            return [f"${val}"]

        case _:
            raise NotImplementedError(f"No emit logic for {type(node).__name__}")
