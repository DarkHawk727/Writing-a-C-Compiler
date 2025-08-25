from frontend.parser import (
    Complement,
    Constant,
    Function,
    Identifier,
    Negation,
    Program,
    Return,
    UnaryOp,
)
from typing import Any, Literal, NamedTuple


def is_namedtuple_instance(x: Any) -> bool:
    return isinstance(x, tuple) and hasattr(x, "_fields")


def is_primitive(x: Any) -> bool:
    return isinstance(x, (str, int, float, bool)) or x is None


def node_label(x: Any) -> str:
    if is_namedtuple_instance(x):
        cls = "**" + x.__class__.__name__ + "**"
        prims = [f"{f}={repr(getattr(x, f))}" for f in x._fields if is_primitive(getattr(x, f))]
        return cls if not prims else cls + "\\n" + "\\n".join(prims)
    if is_primitive(x):
        return repr(x)
    return x.__class__.__name__


def ast_to_mermaid(root: Any) -> str:
    lines = ["graph TD"]
    counter = {"i": 0}

    def new_id() -> str:
        counter["i"] += 1
        return f"n{counter['i']}"

    def visit(x: Any) -> str:
        nid = new_id()
        label = node_label(x).replace('"', '\\"')
        label = label.replace("\\n", "<br/>")
        lines.append(f'\t{nid}["{label}"]')

        if is_namedtuple_instance(x):
            for field in x._fields:
                val = getattr(x, field)
                if is_primitive(val):
                    continue
                if isinstance(val, list):
                    hub = new_id()
                    lines.append(f'\t{hub}["{field}[]"]')
                    lines.append(f"\t{nid} --> {hub}")
                    for i, item in enumerate(val):
                        child = visit(item)
                        lines.append(f"\t{hub} -->|[{i}]| {child}")
                else:
                    child = visit(val)
                    lines.append(f"\t{nid} -->|{field}| {child}")
        elif isinstance(x, list):
            for i, item in enumerate(x):
                child = visit(item)
                lines.append(f"\t{nid} -->|[{i}]| {child}")
        return nid

    visit(root)
    return "\n".join(lines)


def pretty_print_tree(root: NamedTuple, indent=0) -> str:
    spacer = " " * (indent + 2)
    if isinstance(root, list):
        if not root:
            return "[]"
        result = "[\n"
        for item in root:
            result += spacer + pretty_print_tree(item, indent + 2) + ",\n"
        result += " " * (indent) + "]"
        return result
    elif isinstance(root, tuple) and hasattr(root, "_fields"):
        result = f"{type(root).__name__}(\n"
        for field in root._fields:
            value = getattr(root, field)
            result += f"{spacer}{field}="
            result += pretty_print_tree(value, indent + 2)
            result += ",\n"
        result += " " * indent + ")"
        return result
    else:
        return repr(root)
