from __future__ import annotations

from dataclasses import dataclass

import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)


_TRANSFORMS = standard_transformations + (convert_xor, implicit_multiplication_application)


@dataclass(frozen=True)
class ParseLimits:
    max_chars: int = 400
    max_ops: int = 400


_ALLOWED_FUNCS: dict[str, object] = {
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "sec": sp.sec,
    "csc": sp.csc,
    "cot": sp.cot,
    "asin": sp.asin,
    "acos": sp.acos,
    "atan": sp.atan,
    "sinh": sp.sinh,
    "cosh": sp.cosh,
    "tanh": sp.tanh,
    "exp": sp.exp,
    "log": sp.log,
    "ln": sp.log,
    "sqrt": sp.sqrt,
    "Abs": sp.Abs,
    "pi": sp.pi,
    "E": sp.E,
}


def latex(expr: sp.Expr) -> str:
    return sp.latex(expr)


def parse_text_expr(expr_text: str, variable: str = "x", *, limits: ParseLimits | None = None) -> tuple[sp.Expr, sp.Symbol]:
    lim = limits or ParseLimits()
    if not expr_text or not expr_text.strip():
        raise ValueError("Expression is empty.")
    if len(expr_text) > lim.max_chars:
        raise ValueError(f"Expression too long (>{lim.max_chars} characters).")

    x = sp.Symbol(variable)
    local_dict = dict(_ALLOWED_FUNCS)
    local_dict[variable] = x

    expr = parse_expr(expr_text, local_dict=local_dict, transformations=_TRANSFORMS, evaluate=True)
    expr = sp.simplify(expr)
    if sp.count_ops(expr) > lim.max_ops:
        raise ValueError("Expression too complex.")
    return expr, x

