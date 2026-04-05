import type { IntegrateResponse } from "./types";

export async function integrate(expr: string, variable: string): Promise<IntegrateResponse> {
  const res = await fetch("http://localhost:8000/integrate", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ expr, variable }),
  });
  if (!res.ok) {
    throw new Error(`Backend error: ${res.status}`);
  }
  return (await res.json()) as IntegrateResponse;
}
