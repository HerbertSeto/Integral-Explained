from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import sympy as sp

from .schemas import PlotSeries


@dataclass(frozen=True)
class PlotConfig:
    x_min: float = -10.0
    x_max: float = 10.0
    points: int = 401


def _safe_float(v) -> float | None:
    try:
        if v is None:
            return None
        if isinstance(v, complex):
            return None
        fv = float(v)
        if not np.isfinite(fv):
            return None
        return fv
    except Exception:  # noqa: BLE001
        return None


def sample_series(expr: sp.Expr | None, x: sp.Symbol, *, name: str, cfg: PlotConfig) -> PlotSeries:
    xs = np.linspace(cfg.x_min, cfg.x_max, cfg.points)
    ys: list[float | None] = [None] * len(xs)
    if expr is None:
        return PlotSeries(name=name, x=[float(t) for t in xs], y=ys)

    f = sp.lambdify(x, expr, modules=["numpy"])
    for i, t in enumerate(xs):
        try:
            y = f(t)
            if isinstance(y, np.ndarray):
                y = y.item()
            ys[i] = _safe_float(y)
        except Exception:  # noqa: BLE001
            ys[i] = None
    return PlotSeries(name=name, x=[float(t) for t in xs], y=ys)


def build_plots(integrand: sp.Expr, antideriv: sp.Expr | None, x: sp.Symbol) -> list[PlotSeries]:
    cfg = PlotConfig()
    return [
        sample_series(integrand, x, name="f(x)", cfg=cfg),
        sample_series(antideriv, x, name="F(x)", cfg=cfg),
    ]

