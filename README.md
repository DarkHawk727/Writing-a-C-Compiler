# Writing a C Compiler

This repo contains a Python implementation of a C compiler following [Writing a C Compiler by Nora Sandler](https://nostarch.com/writing-c-compiler). The final compiler is located in the X folder. It is ~Y lines of code.

[Eventually, describe the optimizations it makes and maybe some benchmarks and limitations.]

## File Structure

TBA

## Compiler Architecture

```mermaid
flowchart TD
    A@{ shape: doc, label: "program.c" } -->|input| B[Lexer]
    B -->|Token list| D[Parser]
    D -->|AST| SA

    %% Semantic Analysis Subgraph
    subgraph SA[Semantic analysis]
      direction TB
      SA1[Identifier resolution] --> SA2[Type checking] --> SA3[Loop labeling]
    end
    SA -->|Transformed AST| H[TACKY generation]

    H -->|TACKY| OPT

    %% Optimization Subgraph
    subgraph OPT[Optimization]
      direction TB
      O1[Constant folding] --> O2[Unreachable code elimination] --> O3[Copy propagation] --> O4[Dead store elimination]
      O4 --> O1
    end
    OPT -->|Optimized TACKY| AG

    %% Assembly Generation Subgraph
    subgraph AG[Assembly generation]
      direction TB
      AG1[Converting TACKY to assembly] --> AG2[Register allocation] --> AG3[Replacing pseudo-operands] --> AG4[Instruction fix-up]
    end
    AG -->|Assembly| N[Code emission]

    N --> O@{ shape: doc, label: "program.s" }
```

## Limitations

- Can only compile the simplest programs (just returns a single number)

## Usage

```text
usage: main.py [-h] [--stage {lex,parse,tacky,codegen,compile}] file

Compiler with stage selection

positional arguments:
  file                  Input file to process

options:
  -h, --help            show this help message and exit
  --stage {lex,parse,codegen,compile}
                        Select the compiler stage to run (default: compile)
```
