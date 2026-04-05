"use client";

import { useState } from "react";

import styles from "./page.module.css";
import { StepsViewer } from "@/components/StepsViewer";
import { PlotPanel } from "@/components/PlotPanel";
import { MathDisplay } from "@/components/MathDisplay";
import { integrate } from "@/lib/api";

import type { IntegrateResponse } from "@/lib/types";

export default function Home() {
  const [expr, setExpr] = useState("sin(x)");
  const [variable, setVariable] = useState("x");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<IntegrateResponse | null>(null);

  async function onCompute() {
    setLoading(true);
    setError(null);
    try {
      const out = await integrate(expr, variable);
      setData(out);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
      setData(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.page}>
      <main className={styles.main}>
        {/* ── Header ─────────────────────────────────────── */}
        <header className={styles.header}>
          <h1 className={styles.h1}>Integral Explained</h1>
          <p className={styles.subhead}>
            Symbolic integrals with tutor-style steps
          </p>
        </header>

        {/* ── Input card ─────────────────────────────────── */}
        <section className={styles.card}>
          <div className={styles.inputRow}>
            <label className={styles.label}>
              <span className={styles.labelText}>Expression</span>
              <input
                className={styles.input}
                value={expr}
                onChange={(e) => setExpr(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && onCompute()}
                placeholder="e.g. x*exp(x)"
              />
            </label>

            <label className={styles.labelSmall}>
              <span className={styles.labelText}>Variable</span>
              <input
                className={styles.inputSmall}
                value={variable}
                onChange={(e) => setVariable(e.target.value)}
              />
            </label>

            <button className={styles.button} onClick={onCompute} disabled={loading}>
              {loading ? "Computing…" : "Compute"}
            </button>
          </div>
          {error ? <div className={styles.error}>{error}</div> : null}
        </section>

        {/* ── Results ────────────────────────────────────── */}
        {data ? (
          <>
            {/* Result banner */}
            <section className={styles.resultBanner}>
              <div className={styles.resultItem}>
                <span className={styles.resultLabel}>Integral</span>
                <span className={styles.resultMath}>
                  <MathDisplay latex={`\\int ${data.integrandLatex} \\, d${variable}`} block />
                </span>
              </div>
              <div className={styles.resultArrow}>→</div>
              <div className={styles.resultItem}>
                <span className={styles.resultLabel}>Antiderivative</span>
                <span className={styles.resultMath}>
                  <MathDisplay latex={data.resultLatex} block />
                </span>
              </div>
            </section>

            {/* Steps + Graph side by side */}
            <section className={styles.columns}>
              <div className={styles.column}>
                <h2 className={styles.h2}>Steps</h2>
                <StepsViewer steps={data.steps} />
              </div>

              <div className={styles.column}>
                <h2 className={styles.h2}>Graph</h2>
                <PlotPanel series={data.plots} />
              </div>
            </section>
          </>
        ) : null}
      </main>
    </div>
  );
}
