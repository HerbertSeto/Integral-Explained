# Integral Explained

A web app that computes symbolic integrals, plots the integrand and antiderivative, and walks you through the solution step-by-step using an LLM tutor.

![stack](https://img.shields.io/badge/backend-FastAPI%20%2B%20SymPy-blue) ![stack](https://img.shields.io/badge/frontend-Next.js%2019-black) ![stack](https://img.shields.io/badge/LLM-Groq%20(Llama%203.3)-orange)

---

## Features

- **Symbolic integration** — SymPy computes the exact antiderivative and verifies it by differentiation.
- **Tutor-style steps** — When the result is verified, a Groq LLM (Llama 3.3 70B) generates a structured, step-by-step Calc I/II solution (u-substitution, integration by parts, trig substitution, partial fractions, etc.).
- **Interactive plots** — Plotly renders the integrand and antiderivative side-by-side.
- **KaTeX rendering** — All math is displayed as properly typeset LaTeX in the browser.
- **Safe input parsing** — Expression input is validated against an allowlist of functions before being evaluated.

---

## Project Structure

```
Integral-Explained/
├── backend/                  # FastAPI + SymPy API
│   ├── app/
│   │   ├── main.py           # API routes and integration logic
│   │   ├── schemas.py        # Pydantic request/response models
│   │   ├── sympy_utils.py    # Safe expression parser + LaTeX converter
│   │   ├── llm_steps.py      # Groq API call for step generation
│   │   ├── plotting.py       # Numerical sampling for Plotly
│   │   └── steps/engine.py   # (Legacy) rule-based step engine
│   ├── tests/
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── .env.example
└── frontend/                 # Next.js 19 (App Router) + TypeScript
    └── src/
        ├── app/              # Pages and global styles
        ├── components/       # MathDisplay, StepsViewer, PlotPanel
        └── lib/              # API client and TypeScript types
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- A free [Groq API key](https://console.groq.com/)

---

### 1. Backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Set up your API key
copy .env.example .env        # Windows
# cp .env.example .env        # macOS / Linux
# Then open .env and replace the placeholder with your actual GROQ_API_KEY

# Start the development server
python -m uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. You can verify it with:

```
GET http://localhost:8000/health
```

---

### 2. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## API Reference

### `POST /integrate`

**Request body**

```json
{
  "expr": "x * exp(x)",
  "variable": "x"
}
```

**Response**

```json
{
  "stepsAvailable": true,
  "integrandLatex": "x e^{x}",
  "resultLatex": "(x - 1) e^{x}",
  "steps": [
    {
      "title": "Identify the technique",
      "explanation": "The integrand is a product of a polynomial and an exponential, so we use integration by parts.",
      "inputLatex": "\\int x e^{x}\\, dx",
      "outputLatex": null
    }
  ],
  "plots": [...],
  "meta": { "variable": "x" }
}
```

Steps are only included when SymPy can verify the antiderivative. If the LLM call fails or times out, `stepsAvailable` is `false` and `steps` is an empty array.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend framework | [FastAPI](https://fastapi.tiangolo.com/) |
| Symbolic math | [SymPy](https://www.sympy.org/) |
| LLM provider | [Groq](https://groq.com/) — Llama 3.3 70B Versatile |
| Async runtime | [AnyIO](https://anyio.readthedocs.io/) |
| Frontend framework | [Next.js 19](https://nextjs.org/) (App Router) |
| Math rendering | [KaTeX](https://katex.org/) |
| Plotting | [Plotly.js](https://plotly.com/javascript/) via [react-plotly.js](https://github.com/plotly/react-plotly.js) |

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | API key from [console.groq.com](https://console.groq.com/) |

Create `backend/.env` using `backend/.env.example` as a template.

---

## Running Tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```
