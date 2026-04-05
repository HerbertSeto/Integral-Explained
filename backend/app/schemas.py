from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class LLMStep(BaseModel):
    title: str
    explanation: str | None = None
    inputLatex: str | None = None
    outputLatex: str | None = None


class PlotSeries(BaseModel):
    name: str
    x: list[float]
    y: list[float | None]


class IntegrateRequest(BaseModel):
    expr: str = Field(..., description="Expression to integrate, in SymPy-friendly text form.")
    variable: str = Field("x", description="Integration variable.")


class IntegrateResponse(BaseModel):
    stepsAvailable: bool
    integrandLatex: str
    resultLatex: str | None = None
    steps: list[LLMStep] = Field(default_factory=list)
    plots: list[PlotSeries] = Field(default_factory=list)
    meta: dict[str, Any] = Field(default_factory=dict)
