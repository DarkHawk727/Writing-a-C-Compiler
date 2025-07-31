#!/opt/homebrew/bin/python3.10
import argparse
import os
from parser import create_pretty_tuple_str, parse_program

from codegen import convert_AST_to_assembly
from lexer import lex


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

    # Check if the file exists
    if not os.path.isfile(args.file):
        print(f"Error: File '{args.file}' does not exist.")
        return

    with open(args.file, "r") as f:
        program = "".join([line.strip() for line in f.readlines()])

    if args.stage == "lex":
        print(lex(program))
    elif args.stage == "parse":
        print(create_pretty_tuple_str(parse_program(lex(program))))
    elif args.stage == "codegen":
        instructions = convert_AST_to_assembly(parse_program(lex(program)))
        print("\n".join(instructions))
    elif args.stage == "compile":
        with open(f"{args.file[:-2]}.s", "w") as out:
            for instruction in convert_AST_to_assembly(parse_program(lex(program))):
                out.write(instruction + "\n")


if __name__ == "__main__":
    main()
