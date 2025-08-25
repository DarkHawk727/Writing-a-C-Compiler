#!/opt/homebrew/bin/python3.10
import argparse
import os

from backend.codegen import emit_assembly
from backend.tacky2asm import convert_TACKY_to_assembly
from frontend.lexer import lex
from frontend.parser import parse_program
from middle.tacky import convert_AST_to_TACKY
from utils.viz import pretty_print_tree


def main():
    parser = argparse.ArgumentParser(description="Compiler with stage selection")
    parser.add_argument("file", help="Input file to process")
    parser.add_argument(
        "--stage",
        choices=["lex", "parse", "tacky", "codegen", "compile"],
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
        print(pretty_print_tree(parse_program(lex(program))))
    elif args.stage == "tacky":
        print(pretty_print_tree(convert_AST_to_TACKY(parse_program(lex(program)))))
    elif args.stage == "codegen":
        print(
            pretty_print_tree(
                convert_TACKY_to_assembly(
                    convert_AST_to_TACKY(parse_program(lex(program)))
                )
            )
        )
    elif args.stage == "compile":
        with open(f"{args.file[:-2]}.s", "w") as out:
            for instruction in emit_assembly(
                convert_TACKY_to_assembly(
                    convert_AST_to_TACKY(parse_program(lex(program)))
                )
            ):
                out.write(instruction + "\n")


if __name__ == "__main__":
    main()
