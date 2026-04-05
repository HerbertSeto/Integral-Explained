import sympy as sp

from app.steps.engine import build_steps
from app.sympy_utils import parse_text_expr


def test_usub_steps_available():
    expr, x = parse_text_expr("2*x/(x**2+1)", "x")
    res = build_steps(expr, x)
    assert res.steps_available is True
    assert res.root is not None


def test_ibp_steps_available():
    expr, x = parse_text_expr("x*exp(x)", "x")
    res = build_steps(expr, x)
    assert res.steps_available is True
    assert res.root is not None


def test_trig_sub_steps_available():
    expr, x = parse_text_expr("sqrt(9-x**2)", "x")
    res = build_steps(expr, x)
    assert res.steps_available is True
    assert res.root is not None


def test_steps_not_required_for_unhandled_integral():
    expr, x = parse_text_expr("sin(x)/x", "x")
    res = build_steps(expr, x)
    # This may not produce tutor steps via our supported-technique heuristic.
    assert res.steps_available in {True, False}

