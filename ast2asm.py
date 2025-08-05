from parser import Constant, Function, Identifier, Program, Return
from typing import Any, List, NamedTuple

AssemblyFunction = NamedTuple(
    "AssemblyFunction", [("name", str), ("instructions", List[Any])]
)  # Should ideally remove the Any
AssemblyProgram = NamedTuple(
    "AssemblyProgram", [("function_definition", AssemblyFunction)]
)
AssemblyImmediate = NamedTuple("AssemblyImmediate", [("value", int | str)])
AssemblyMov = NamedTuple("AssemblyMov", [("exp", AssemblyImmediate), ("Register", str)])
AssemblyPop = NamedTuple("AssemblyPop", [("Register", str)])
AssemblyRet = NamedTuple("AssemblyRet", [])


def visit_program(node: Program) -> AssemblyProgram:
    func = visit_function(node.function_definition)
    return AssemblyProgram(func)


def visit_function(node: Function) -> AssemblyFunction:
    instrs = [
        AssemblyMov(AssemblyImmediate("rsp"), "rbp"),
        visit_return(node.body)[0],
        AssemblyPop("rbp"),
        AssemblyRet(),
    ]
    return AssemblyFunction(node.name.name, instrs)


def visit_return(node: Return) -> List:
    return visit_constant(node.return_val)


def visit_constant(node: Constant) -> List:
    # movl $val, %eax → AssemblyMov(AssemblyImmediate(val), 'eax')
    return [AssemblyMov(AssemblyImmediate(node.val), "eax")]


def convert_AST_to_assembly(node: Program) -> AssemblyProgram:
    match node:
        case Program(main_func):
            func = visit_function(main_func)
            return AssemblyProgram(func)

        case Function(name, body):
            instrs = [
                AssemblyMov(AssemblyImmediate("rsp"), "rbp"),
                visit_return(body)[0],
            ]
            return AssemblyFunction(name.name, instrs)

        case Return(return_val):
            return visit_constant(return_val)

        case Constant(val):
            return [AssemblyMov(AssemblyImmediate(val), "eax")]

        case Identifier():
            return []  # still nothing

        case _:
            raise NotImplementedError(f"No visit method for {type(node).__name__}")
