from typing import List

from ast2asm import (
    AssemblyFunction,
    AssemblyImmediate,
    AssemblyMov,
    AssemblyPop,
    AssemblyProgram,
    AssemblyRet,
)


def emit_assembly(node: AssemblyProgram | AssemblyFunction) -> List[str]:
    match node:
        case AssemblyProgram(function_definition=func):
            return emit_assembly(func)

        case AssemblyFunction(name=name, instructions=instructions):
            lines = [f".globl {name}", f"_{name}:"]
            for instr in instructions:
                lines.extend(emit_assembly(instr))
            return lines

        case AssemblyMov(exp=exp, Register=reg):
            exp_code = emit_assembly(exp)[0]
            if reg == "eax":
                return [f"\tmovl  {exp_code}, %eax"]
            elif (
                reg == "rbp"
                and isinstance(exp, AssemblyImmediate)
                and exp.value == "rsp"
            ):
                return ["\tpushq  %rbp", "\tmovq  %rsp, %rbp"]
            else:
                return [f"\tmovq  {exp_code}, %{reg}"]

        case AssemblyImmediate(value=v):
            return [f"${v}"]

        case AssemblyPop(Register=reg):
            return [f"\tpopq  %{reg}"]

        case AssemblyRet():
            return ["\tretq"]

        case _:
            raise NotImplementedError(f"No emit logic for {type(node).__name__}")
