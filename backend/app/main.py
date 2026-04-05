from __future__ import annotations

import os

import anyio
import sympy as sp
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .llm_steps import fetch_llm_steps
from .plotting import build_plots
from .schemas import IntegrateRequest, IntegrateResponse
from .sympy_utils import ParseLimits, latex, parse_text_expr

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

app = FastAPI(title="Integral Explained API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/integrate", response_model=IntegrateResponse)
async def integrate(req: IntegrateRequest) -> IntegrateResponse:
    try:
        expr, x = parse_text_expr(req.expr, req.variable, limits=ParseLimits())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    async def _compute() -> IntegrateResponse:
        try:
            antideriv = await anyio.to_thread.run_sync(sp.integrate, expr, x)
        except Exception:  # noqa: BLE001
            antideriv = None

        integrand_latex = latex(expr)
        result_latex = latex(antideriv) if antideriv is not None else None

        verified = False
        if antideriv is not None:
            try:
                def _verify() -> bool:
                    check = sp.simplify(sp.diff(antideriv, x) - expr)
                    return check == 0

                verified = await anyio.to_thread.run_sync(_verify)
            except Exception:  # noqa: BLE001
                verified = False

        steps = []
        steps_available = False
        steps_error: str | None = None
        if verified and result_latex:
            try:
                steps = await fetch_llm_steps(integrand_latex, result_latex, req.variable)
                steps_available = bool(steps)
            except Exception as e:  # noqa: BLE001
                steps_error = str(e)

        meta: dict = {"variable": req.variable}
        if steps_error:
            meta["stepsError"] = steps_error

        plots = await anyio.to_thread.run_sync(build_plots, expr, antideriv, x)

        return IntegrateResponse(
            stepsAvailable=steps_available,
            integrandLatex=integrand_latex,
            resultLatex=result_latex,
            steps=steps,
            plots=plots,
            meta=meta,
        )

    try:
        with anyio.fail_after(12):
            return await _compute()
    except TimeoutError as e:
        raise HTTPException(status_code=408, detail="Computation timed out.") from e
