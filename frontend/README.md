# Integral Explained — Frontend

Next.js 19 (App Router) frontend for the Integral Explained calculator.

See the [root README](../README.md) for full setup instructions and project overview.

## Quick start

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). The backend must be running on port 8000.

## Key directories

```
src/
├── app/
│   ├── page.tsx            # Main calculator page
│   ├── page.module.css     # Page-scoped styles
│   ├── layout.tsx          # Root layout + metadata
│   └── globals.css         # Global CSS reset and base styles
├── components/
│   ├── MathDisplay.tsx     # KaTeX LaTeX renderer
│   ├── StepsViewer.tsx     # Renders LLM step-by-step solution
│   └── PlotPanel.tsx       # Plotly integrand / antiderivative graph
└── lib/
    ├── api.ts              # fetch wrapper for POST /integrate
    └── types.ts            # TypeScript types mirroring backend schemas
```
