from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable
from uuid import uuid4

import sympy as sp
from sympy.integrals.manualintegrate import integral_steps

from ..schemas import StepNode, StepRule
from ..sympy_utils import latex


@dataclass(frozen=True)
class StepResult:
    steps_available: bool
    root: StepNode | None
    meta: dict[str, Any]


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:10]}"


def _iter_rule_tree(rule: Any) -> Iterable[Any]:
    stack = [rule]
    while stack:
        r = stack.pop()
        yield r
        for v in getattr(r, "__dict__", {}).values():
            if isinstance(v, list):
                for item in v:
                    if _looks_like_rule(item):
                        stack.append(item)
            elif _looks_like_rule(v):
                stack.append(v)


def _looks_like_rule(obj: Any) -> bool:
    return obj is not None and obj.__class__.__module__.endswith("manualintegrate")


def _is_supported_technique(rule: Any) -> bool:
    names = {r.__class__.__name__ for r in _iter_rule_tree(rule)}
    return bool(
        {"URule", "PartsRule", "SqrtQuadraticRule"} & names
    )  # u-sub, IBP, trig-sub (via sqrt quadratic patterns)


def _pick_alternative(rule: Any) -> Any:
    if rule.__class__.__name__ != "AlternativeRule":
        return rule
    alts = getattr(rule, "alternatives", []) or []
    if not alts:
        return rule
    best = None
    for a in alts:
        if best is None:
            best = a
        if _is_supported_technique(a):
            return a
    return best


def _rule_to_step(rule: Any) -> StepNode:
    rule = _pick_alternative(rule)
    cls = rule.__class__.__name__
    integrand = getattr(rule, "integrand", None)
    variable = getattr(rule, "variable", None)
    input_latex = latex(integrand) if integrand is not None else None

    def child(r: Any) -> StepNode:
        return _rule_to_step(r)

    title = cls
    explanation: str | None = None
    out_latex: str | None = None
    step_rule = StepRule.REWRITE
    children: list[StepNode] = []

    if cls == "URule":
        step_rule = StepRule.USUB
        u_func = getattr(rule, "u_func", None)
        u_var = getattr(rule, "u_var", None)
        title = "u-substitution"
        explanation = f"Let {latex(u_var)} = {latex(u_func)} and rewrite the integral in terms of {latex(u_var)}."
        sub = getattr(rule, "substep", None)
        if sub is not None:
            children = [child(sub)]
    elif cls == "PartsRule":
        step_rule = StepRule.IBP
        u = getattr(rule, "u", None)
        dv = getattr(rule, "dv", None)
        title = "integration by parts"
        explanation = f"Choose u = {latex(u)} and dv = {latex(dv)}, then apply ∫u·dv = u·v − ∫v·du."
        v_step = getattr(rule, "v_step", None)
        second_step = getattr(rule, "second_step", None)
        if v_step is not None:
            children.append(StepNode(id=_new_id('ibp_v'), title="compute v = ∫dv", explanation=None, inputLatex=latex(dv), outputLatex=None, rule=StepRule.REWRITE, children=[child(v_step)], checks=[]))
        if second_step is not None:
            children.append(StepNode(id=_new_id('ibp_rest'), title="integrate the remaining integral", explanation=None, inputLatex=None, outputLatex=None, rule=StepRule.REWRITE, children=[child(second_step)], checks=[]))
    elif cls == "SqrtQuadraticRule":
        step_rule = StepRule.TRIG_SUB
        a = getattr(rule, "a", None)
        b = getattr(rule, "b", None)
        c = getattr(rule, "c", None)
        title = "trigonometric substitution"
        explanation = "Use a trig substitution to handle a square-root quadratic (e.g., √(a²−x²), √(a²+x²), √(x²−a²))."
        out_latex = None
        meta_bits = []
        if a is not None and b is not None and c is not None:
            meta_bits.append(f"a={a}, b={b}, c={c}")
        if meta_bits:
            explanation += f" ({', '.join(meta_bits)})"
    elif cls == "RewriteRule":
        step_rule = StepRule.REWRITE
        rewritten = getattr(rule, "rewritten", None)
        title = "rewrite the integrand"
        explanation = "Rewrite the integrand into a form that is easier to integrate."
        if rewritten is not None:
            out_latex = latex(rewritten)
        sub = getattr(rule, "substep", None)
        if sub is not None:
            children = [child(sub)]
    elif cls == "AddRule":
        step_rule = StepRule.REWRITE
        title = "split into a sum of integrals"
        explanation = "Use linearity: integrate each term separately."
        subs = getattr(rule, "substeps", None) or []
        children = [child(s) for s in subs if s is not None]
    elif cls == "ConstantTimesRule":
        step_rule = StepRule.REWRITE
        const = getattr(rule, "constant", None)
        other = getattr(rule, "other", None)
        title = "factor out a constant"
        explanation = f"Pull out the constant {latex(const)} and integrate the remaining expression."
        if other is not None:
            out_latex = latex(other)
        sub = getattr(rule, "substep", None)
        if sub is not None:
            children = [child(sub)]
    elif cls in {"ReciprocalRule", "PowerRule", "ExpRule", "SinRule", "CosRule", "ArctanRule", "ArcsinRule", "ArccosRule"}:
        step_rule = StepRule.REWRITE
        title = "apply a basic antiderivative rule"
        explanation = "Recognize a standard form and apply the corresponding antiderivative."
    else:
        sub = getattr(rule, "substep", None)
        if sub is not None:
            children = [child(sub)]

    if variable is not None and input_latex is not None and variable.free_symbols:
        pass

    return StepNode(
        id=_new_id("step"),
        title=title,
        explanation=explanation,
        inputLatex=input_latex,
        outputLatex=out_latex,
        rule=step_rule,
        children=children,
        checks=[],
    )


def build_steps(expr: sp.Expr, x: sp.Symbol) -> StepResult:
    try:
        rule = integral_steps(expr, x)
    except Exception as e:  # noqa: BLE001
        return StepResult(steps_available=False, root=None, meta={"manualintegrate_error": str(e)})

    if rule is None:
        return StepResult(steps_available=False, root=None, meta={})

    supported = _is_supported_technique(rule)
    root = _rule_to_step(rule)
    return StepResult(steps_available=supported, root=root, meta={"ruleType": rule.__class__.__name__})

