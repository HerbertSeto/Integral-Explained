from __future__ import annotations

import json
import os
from typing import Any

from groq import AsyncGroq

from .schemas import LLMStep

_SYSTEM_PROMPT = """\
You are a Calculus I/II tutor. Given an integral and its verified antiderivative, \
explain how to compute the integral step by step using standard techniques \
(u-substitution, integration by parts, trig substitution, partial fractions, \
or basic rules).

Respond ONLY with a valid JSON array of step objects. Each object must have:
  "title"       : short name for the step (e.g. "Apply u-substitution")
  "explanation" : 1-3 sentences in plain English explaining what is done and why
  "inputLatex"  : LaTeX expression at the start of this step (or null)
  "outputLatex" : LaTeX expression produced by this step (or null)

Do not include any text outside the JSON array. Do not wrap it in markdown fences.\
"""


def _user_prompt(integrand_latex: str, result_latex: str, variable: str) -> str:
    return (
        f"Integral: \\int {integrand_latex} \\, d{variable}\n"
        f"Verified antiderivative: {result_latex}\n\n"
        "Output the JSON step array now."
    )


async def fetch_llm_steps(
    integrand_latex: str,
    result_latex: str,
    variable: str,
) -> list[LLMStep]:
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set.")

    client = AsyncGroq(api_key=api_key)

    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": _user_prompt(integrand_latex, result_latex, variable)},
        ],
        temperature=0.2,
        max_tokens=1500,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content or ""

    # Groq json_object wraps in {"steps": [...]} or similar — handle both
    try:
        parsed = json.loads(content)
        if isinstance(parsed, list):
            raw_list = parsed
        elif isinstance(parsed, dict):
            raw_list = next(
                (v for v in parsed.values() if isinstance(v, list)), []
            )
        else:
            raw_list = []
    except json.JSONDecodeError:
        raw_list = []

    steps: list[LLMStep] = []
    for item in raw_list:
        if not isinstance(item, dict):
            continue
        steps.append(
            LLMStep(
                title=str(item.get("title", "Step")),
                explanation=item.get("explanation") or None,
                inputLatex=item.get("inputLatex") or None,
                outputLatex=item.get("outputLatex") or None,
            )
        )
    return steps
