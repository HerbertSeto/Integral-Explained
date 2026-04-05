"use client";

import dynamic from "next/dynamic";

import type { PlotSeries } from "@/lib/types";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

export function PlotPanel({ series }: { series: PlotSeries[] }) {
  if (!series?.length) return null;

  return (
    <Plot
      data={series.map((s) => ({
        x: s.x,
        y: s.y,
        type: "scatter",
        mode: "lines",
        name: s.name,
        connectgaps: false,
      }))}
      layout={{
        autosize: true,
        height: 360,
        margin: { l: 48, r: 18, t: 12, b: 40 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        font: { color: "rgba(229,231,235,0.92)" },
        xaxis: { zerolinecolor: "rgba(255,255,255,0.10)", gridcolor: "rgba(255,255,255,0.06)" },
        yaxis: { zerolinecolor: "rgba(255,255,255,0.10)", gridcolor: "rgba(255,255,255,0.06)" },
        legend: { orientation: "h" },
      }}
      config={{ displayModeBar: false, responsive: true }}
      style={{ width: "100%" }}
    />
  );
}

