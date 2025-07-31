from parser import Constant, Function, Identifier, Program, Return
from typing import List


def visit_program(node: Program) -> List[str]:
    return visit_function(node.main_func)


def visit_function(node: Function) -> List[str]:
    assembly = [
        f"_{node.name.name}:",
        "\tpushq  %rbp",
        "\tmovq  %rsp, %rbp",
    ]
    assembly.extend(visit_return(node.body))
    assembly.extend(
        [
            "\tpopq  %rbp",
            "\tretq",
        ]
    )
    return assembly


def visit_return(node: Return) -> List[str]:
    return visit_constant(node.return_val)


def visit_constant(node: Constant) -> List[str]:
    return [f"\tmovl  ${node.val}, %eax"]


def convert_AST_to_assembly(node: Program) -> List[str]:
    match node:
        case Program(main_func):
            return visit_function(main_func)
        case Function(name, body):
            assembly = [
                f"_{name.name}:",
                "\tpushq  %rbp",
                "\tmovq  %rsp, %rbp",
            ]
            assembly.extend(visit_return(body))
            assembly.extend(
                [
                    "\tpopq  %rbp",
                    "\tretq",
                ]
            )
            return assembly
        case Return(return_val):
            return visit_constant(return_val)
        case Constant(val):
            return [f"\tmovl  ${val}, %eax"]
        case Identifier():
            return []  # Identifier alone doesn't generate assembly
        case _:
            raise NotImplementedError(f"No visit method for {type(node).__name__}")
