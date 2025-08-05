#!/opt/homebrew/bin/python3.10
import argparse
import os
from parser import parse_program
from typing import NamedTuple

from ast2asm import convert_AST_to_assembly
from codegen import emit_assembly
from lexer import lex


def create_pretty_tuple_str(obj: NamedTuple, indent=0) -> str:
    spacer = " " * (indent + 2)
    if isinstance(obj, list):
        if not obj:
            return "[]"
        result = "[\n"
        for item in obj:
            result += spacer + create_pretty_tuple_str(item, indent + 2) + ",\n"
        result += " " * (indent) + "]"
        return result
    elif isinstance(obj, tuple) and hasattr(obj, "_fields"):
        result = f"{type(obj).__name__}(\n"
        for field in obj._fields:
            value = getattr(obj, field)
            result += f"{spacer}{field}="
            result += create_pretty_tuple_str(value, indent + 2)
            result += ",\n"
        result += " " * indent + ")"
        return result
    else:
        return repr(obj)


def main():
    parser = argparse.ArgumentParser(description="Compiler with stage selection")
    parser.add_argument("file", help="Input file to process")
    parser.add_argument(
        "--stage",
        choices=["lex", "parse", "codegen", "compile"],
        default="compile",
        help="Select the compiler stage to run (default: compile)",
    )

    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print(f"Error: File '{args.file}' does not exist.")
        return

    with open(args.file, "r") as f:
        program = "".join([line.strip() for line in f.readlines()])

    if args.stage == "lex":
        print(*lex(program), sep="\n")
    elif args.stage == "parse":
        print(create_pretty_tuple_str(parse_program(lex(program))))
    elif args.stage == "codegen":
        print(
            create_pretty_tuple_str(
                convert_AST_to_assembly(parse_program(lex(program)))
            )
        )
    elif args.stage == "compile":
        with open(f"{args.file[:-2]}.s", "w") as out:
            for instruction in emit_assembly(
                convert_AST_to_assembly(parse_program(lex(program)))
            ):
                out.write(instruction + "\n")


if __name__ == "__main__":
    main()
